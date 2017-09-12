from django.views import generic
from django.utils import timezone
from django.contrib import messages
from ...models.zipline_app.order import Order
from ...utils import redirect_index_or_local, now_minute

from ...forms import OrderForm, OrderDocumentForm
from django.urls import  reverse_lazy
from django.core.exceptions import PermissionDenied

# https://django-tables2.readthedocs.io/en/latest/pages/tutorial.html
from django_tables2 import RequestConfig
from ...tables import OrderTable

# django-tables2: Filtering data in your table
# https://django-tables2.readthedocs.io/en/latest/pages/filtering.html
from django_tables2 import SingleTableView
from django_filters.views import FilterView
from ...filters import OrderFilter
from ...models.zipline_app.asset import Asset
from ...models.zipline_app.account import Account
from ...models.zipline_app.side import OPEN, FILLED, CANCELLED, PLACED
from ...download_builder import DownloadBuilder
from django.http import HttpResponseRedirect

class OrderCreate(generic.CreateView):
  model = Order
  template_name = 'zipline_app/order/order_form.html'
  form_class = OrderForm

  def form_valid(self, form):
    order = form.save(commit=False)
    if self.request.user.is_authenticated():
      order.user = self.request.user
    return super(OrderCreate, self).form_valid(form)

  def get_success_url(self):
    # django message levels
    # https://docs.djangoproject.com/en/1.10/ref/contrib/messages/#message-levels
    messages.add_message(self.request, messages.INFO, "Successfully created order: %s" % self.object)
    return redirect_index_or_local(self,'zipline_app:orders-list')

  def get_initial(self):
    initial = super(OrderCreate, self).get_initial()
    initial['pub_date'] = now_minute()
    initial['source'] = self.request.GET.get('source',None)
    return initial

class FilteredSingleTableView(SingleTableView):
  filter_class = None
  table_pagination = {'per_page': 15}

  def get_table_data(self):
    data = super(FilteredSingleTableView, self).get_table_data()
    self.filter = self.filter_class(self.request.GET, queryset=data)
    return self.filter.qs

  def get_context_data(self, **kwargs):
    context = super(FilteredSingleTableView, self).get_context_data(**kwargs)
    context['filter'] = self.filter
    return context

def get_stats_orders():
  temp = Order()
  out = [
    {
      'display': 'All',
      'key': '',
      'value': Order.objects.all().count()
    },
    {
      'display': temp.get_order_status_display(OPEN),
      'key': OPEN,
      'value': Order.objects.filter(fill__isnull=True, placement__isnull=True).count()
    },
    {
      'display': temp.get_order_status_display(PLACED),
      'key': PLACED,
      'value': Order.objects.filter(fill__isnull=True, placement__isnull=False).count()
    },
    {
      'display': temp.get_order_status_display(FILLED),
      'key': FILLED,
      'value': Order.objects.filter(fill__isnull=False).count()
    },
  ]
  return out

class OrderList(FilteredSingleTableView):
  #template_name = 'zipline_app/order/order_list.html'
  # template_name = 'zipline_app/order_filter.html'
  source="orders-list"
  table_class = OrderTable
  model = Order
  filter_class = OrderFilter
  ordering = ['-pub_date']

  def get_context_data(self, **kwargs):
    context = super(OrderList, self).get_context_data(**kwargs)
    context['filters_actual'] = self._get_filters_actual()

    context['stats_orders'] = get_stats_orders()

    return context

  def _get_filters_actual(self):
    # append variable for filters

    # Instead of accessing GET directly, use self.filter.data
    # http://stackoverflow.com/questions/20886293/ddg#20909497
    # filters = {x: self.request.GET.get(x,None) for x in terms}
    # self.filters yields OrderFilter
    # filters = {x: self.filter.data.get(x) for x in terms}
    filters = self.filter.data

    # drop empty filtering
    filters = {k: filters[k] for k in filters if filters[k]}

    # convert from keys to model objects or displayable strings
    if 'asset' in filters:
      filters['asset'] = Asset.objects.get(id=filters['asset'])

    if 'account' in filters:
      filters['account'] = Account.objects.get(id=filters['account'])

    if 'order_status' in filters:
      temp = Order()
      filters['order_status'] = temp.get_order_status_display(filters['order_status'])

    if 'order_side' in filters:
      temp = Order()
      temp.order_side = filters['order_side']
      filters['order_side'] = temp.get_order_side_display()

    return filters

class OrderDelete(generic.DeleteView):
  model = Order
  template_name = 'zipline_app/order/order_confirm_delete.html'

  def get_success_url(self):
    messages.add_message(self.request, messages.INFO, "Successfully deleted order: %s" % self.object)
    return redirect_index_or_local(self,'zipline_app:orders-list')

  def get_object(self, *args, **kwargs):
    obj = super(OrderDelete, self).get_object(*args, **kwargs)
    if not (obj.user == self.request.user and len(obj.fills())==0):
      raise PermissionDenied
    return obj

class OrderDetailView(generic.DetailView):
    model = Order
    template_name = 'zipline_app/order/order_detail.html'

# https://django-reversion.readthedocs.io/en/stable/views.html#reversion-views-revisionmixin
from reversion.views import RevisionMixin
class OrderUpdateView(RevisionMixin, generic.UpdateView):
  model = Order
  form_class = OrderForm
  template_name = 'zipline_app/order/order_form.html'

  def get_success_url(self):
    # django message levels
    # https://docs.djangoproject.com/en/1.10/ref/contrib/messages/#message-levels
    messages.add_message(self.request, messages.INFO, "Successfully updated order: %s" % self.object)
    local = reverse_lazy('zipline_app:orders-detail', args=(self.object.id,))
    return redirect_index_or_local(self, local)

  def get_object(self, *args, **kwargs):
    obj = super(OrderUpdateView, self).get_object(*args, **kwargs)
    if not (obj.user == self.request.user and len(obj.fills())==0):
      raise PermissionDenied
    return obj

  def get_context_data(self, **kwargs):
    context = super(OrderUpdateView, self).get_context_data(**kwargs)
    context['docs_form'] = OrderDocumentForm()
    return context

class OrderDownloadView(generic.ListView):
  def get(self, *args, **kwargs):
    orders = Order.objects.all()
    builder = DownloadBuilder()
    df = builder.orders2df(orders)
    full_name = builder.df2xlsx(df)
    response = builder.fn2response(full_name)
    return response

from ..._mayanManager import MayanManager
from django.conf import settings
class OrderDocumentUploadView(generic.edit.FormView):
  template_name = 'zipline_app/order/order_document_upload.html'
  form_class = OrderDocumentForm
  
  def get_success_url(self):
    order_id = self.kwargs['pk']
    return reverse_lazy('zipline_app:orders-detail', args=(order_id,))

  # need to append 'order' in case of form failure, so that "order.id" in the order_document_upload.html is not empty
  def get_context_data(self, **kwargs):
    context = super(OrderDocumentUploadView, self).get_context_data(**kwargs)
    context['order'] = Order.objects.get(id=self.kwargs['pk'])
    context['docs_form'] = OrderDocumentForm()
    return context

  def post(self, request, *args, **kwargs):
    #username = None
    if not request.user.is_authenticated():
      raise Exception("Access denied")
    #username = request.user.username

    order_id = self.kwargs['pk']
    if not order_id:
      raise Exception("Submitting form without order id")

    form_class = self.get_form_class()
    form = self.get_form(form_class)
    files = request.FILES.getlist('docfile')
    if form.is_valid():
      mayanMan = MayanManager(
        host=settings.MAYAN_HOST,
        username=settings.MAYAN_ADMIN_USER,
        password=settings.MAYAN_ADMIN_PASSWORD
      )
      if mayanMan.api is None:
        raise Exception("Failed to connect to mayan edms")

      tag_label = mayanMan.order_id_to_tag(order_id)
      tag_obj = mayanMan.create_tag_if_not(tag_label)
      doc_ids = []
      for f in files:
        response = mayanMan.upload_doc(f, tag_obj)
        doc_ids.append(response['id'])

      mayanMan.attach_docs_to_tag(tag_obj, doc_ids)
      return self.form_valid(form)
    else:
      return self.form_invalid(form)


def delete_doc_view(request, order_id, doc_id):
  if not request.user.is_authenticated():
    raise Exception("Access denied")

  mayanMan = MayanManager(
    host=settings.MAYAN_HOST,
    username=settings.MAYAN_ADMIN_USER,
    password=settings.MAYAN_ADMIN_PASSWORD
  )

  mayanMan.delete_doc(doc_id)

  url = reverse_lazy('zipline_app:orders-detail', args=(order_id,))
  return HttpResponseRedirect(url)

