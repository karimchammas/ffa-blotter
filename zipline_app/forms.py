from .models.zipline_app.fill import Fill
from .models.zipline_app.order import Order
from .models.zipline_app.asset import Asset

from .widgets import AssetModelSelect2Widget, AccountModelSelect2Widget, ReadOnlyWidgetSimple, ReadOnlyWidgetAsset, ReadOnlyWidgetOrder, ReadOnlyWidgetOrderSide, OrderQtyUnitWidget
from django import forms

# override widget in createview
# http://stackoverflow.com/a/21407374/4126114
# Override a Django generic class-based view widget
# http://stackoverflow.com/a/27322032/4126114
class FillForm(forms.ModelForm):
  source=forms.CharField(required=False, widget = forms.HiddenInput())
  field_order = [
    'pub_date', 'dedicated_to_order', 'fill_side', 'fill_qty_unsigned', 'asset',
    'fill_price', 'fill_status', 'category', 'is_internal', 'trade_date', 'fill_text'
  ]
  class Meta:
    model=Fill
    exclude = ["user"]
    widgets = {
      'pub_date': ReadOnlyWidgetSimple(),
      'dedicated_to_order': ReadOnlyWidgetOrder(),
      # 'asset': AssetModelSelect2Widget(),
      'asset': ReadOnlyWidgetAsset(),
      'fill_side': ReadOnlyWidgetOrderSide(),
      'fill_qty_unsigned': ReadOnlyWidgetSimple(),
    }
  def clean_pub_date(self): return self.initial['pub_date'] #.strftime("%Y-%m-%d %H:%i:%s")
  def clean_dedicated_to_order(self): return self.initial['dedicated_to_order']
  def clean_asset(self):
    aid = self.initial['asset']
    if not isinstance(aid, int): return aid
    return Asset.objects.get(id=aid)
  def clean_fill_side(self): return self.initial['fill_side']
  def clean_fill_qty_unsigned(self): return self.initial['fill_qty_unsigned']
  def clean_source(self): return self.initial['source'] if 'source' in self.initial else None

class OrderForm(forms.ModelForm):
  source=forms.CharField(required=False, widget = forms.HiddenInput())
  field_order = [
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

  class Meta:
    model=Order
    exclude=['user','order_status']
    widgets = {
      'pub_date': ReadOnlyWidgetSimple(),
      'asset': AssetModelSelect2Widget(),
      'account': AccountModelSelect2Widget(),
      'order_qty_unit': OrderQtyUnitWidget(),
    }
  def clean_pub_date(self): return self.initial['pub_date'] #.strftime("%Y-%m-%d %H:%i:%s")
  def clean_source(self): return self.initial['source'] if 'source' in self.initial else None

