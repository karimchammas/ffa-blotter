# https://pypi.python.org/pypi/django-filter
import django_filters
from .models.zipline_app.order import Order
from .models.zipline_app.asset import Asset
from .models.zipline_app.account import Account
from .forms import OrderForm
from .widgets import AssetModelSelect2Widget

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

  class Meta:
    model = Order
    fields = ['order_status', 'asset', 'account', 'order_side']

