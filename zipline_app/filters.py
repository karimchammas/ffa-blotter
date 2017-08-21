# https://pypi.python.org/pypi/django-filter
import django_filters
from .models.zipline_app.order import Order
from .models.zipline_app.asset import Asset
from .models.zipline_app.account import Account
from .forms import OrderForm
from .widgets import AssetModelSelect2Widget
from .models.zipline_app.side import ORDER_STATUS_CHOICES

class OrderFilter(django_filters.FilterSet):
  asset = django_filters.ModelChoiceFilter(
      # Funny enough, ".filter(...False)" will yield an error
      queryset = Asset.objects.exclude(order__isnull=True),
      widget=AssetModelSelect2Widget()
  )
  account = django_filters.ModelChoiceFilter(
      queryset = Account.objects.exclude(order__isnull=True),
      widget=OrderForm.Meta.widgets['account']
  )
  order_status = django_filters.ChoiceFilter(
    choices = ORDER_STATUS_CHOICES,
    label='Order status',
    method='filter_order_status'
  )

  class Meta:
    model = Order
    fields = ['asset', 'account', 'order_side']

  def filter_order_status(self, queryset, name, value):
    filtered_ids = [x.id for x in queryset if x.order_status == value]
    return queryset.filter(id__in = filtered_ids)


from .models.zipline_app.custodian import Custodian
class CustodianFilter(django_filters.FilterSet):
  custodian_name = django_filters.CharFilter(lookup_expr='icontains')

  class Meta:
    model = Custodian
    fields = ['custodian_name', ]
