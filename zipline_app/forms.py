from .models.zipline_app.fill import Fill
from .models.zipline_app.order import Order
from .widgets import AssetModelSelect2Widget, AccountModelSelect2Widget
from django import forms

# override widget in createview
# http://stackoverflow.com/a/21407374/4126114
# Override a Django generic class-based view widget
# http://stackoverflow.com/a/27322032/4126114
class FillForm(forms.ModelForm):
  source=forms.CharField(required=False, widget = forms.HiddenInput())
  class Meta:
    model=Fill
    fields = [
      'pub_date', 'asset', 'fill_side', 'fill_qty_unsigned', 'fill_price', 'fill_text', 'tt_order_key',
      'dedicated_to_order',
      'status', 'category', 'is_internal'
    ]
    widgets = {
      'asset': AssetModelSelect2Widget()
    }

class OrderForm(forms.ModelForm):
  source=forms.CharField(required=False, widget = forms.HiddenInput())
  class Meta:
    model=Order
    fields = [
      'pub_date',
      'asset',
      'account',
      'am_type',
      'order_type',
      'limit_price',
      'order_validity',
      'validity_date',
      'order_side',
      'order_qty_unsigned',
      'order_qty_unit',
      'order_text',
      'commission'
    ]
    widgets = {
      'asset': AssetModelSelect2Widget(),
      'account': AccountModelSelect2Widget(),
    }
