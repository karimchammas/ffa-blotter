from django.views import generic
from django.utils import timezone
from django.contrib import messages
from ...models.zipline_app.order import Order
from ...utils import redirect_index_or_local, now_minute

from ...forms import OrderForm
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
  out = [
    {
      'display': 'Total',
      # 'key': 'T',
      'value': Order.objects.all().count()
    },
    {
      'display': 'Open',
      'key': 'O',
      'value': Order.objects.filter(fill__isnull=True, placement__isnull=True).count()
    },
    {
      'display': 'Placed',
      # 'key': 'P',
      'value': Order.objects.filter(fill__isnull=True, placement__isnull=False).count()
    },
    {
      'display': 'Filled',
      'key': 'F',
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
    # self.filters yields OrderFilter
    terms = self.filter.Meta.fields

    # Instead of accessing GET directly, use self.filter.data
    # http://stackoverflow.com/questions/20886293/ddg#20909497
    # filters = {x: self.request.GET.get(x,None) for x in terms}
    filters = {x: self.filter.data.get(x) for x in terms}

    # drop empty filtering
    filters = {k: filters[k] for k in filters if filters[k]}

    # convert from keys to model objects or displayable strings
    if 'asset' in filters:
      filters['asset'] = Asset.objects.get(id=filters['asset'])

    if 'account' in filters:
      filters['account'] = Account.objects.get(id=filters['account'])

    if 'order_status' in filters:
      temp = Order()
      temp.order_status = filters['order_status']
      filters['order_status'] = temp.get_order_status_display()

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
    def get_queryset(self):
        """
        Excludes any orders that aren't published yet.
        """
        return Order.objects.filter(pub_date__lte=timezone.now())

class OrderUpdateView(generic.UpdateView):
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

