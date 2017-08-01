from django.views import generic
from django.utils import timezone
from django.contrib import messages
from ...models.zipline_app.order import Order
from ...utils import redirect_index_or_local, now_minute

from ...forms import OrderForm
from django.urls import  reverse_lazy
from django.core.exceptions import PermissionDenied

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

class OrderList(generic.ListView):
  template_name = 'zipline_app/order/order_list.html'
  context_object_name='order_list'
  source="orders-list"
  def get_queryset(self):
    return Order.objects.all()

  def get_context_data(self, *args, **kwargs):
    context = super(OrderList, self).get_context_data(*args, **kwargs)
    view = OrderCreate()
    form = view.get_form_class()
    context["order_form"]=form
    return context

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

