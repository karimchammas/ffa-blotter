from .models.zipline_app.fill import Fill
from .models.zipline_app.order import Order
from .models.zipline_app.asset import Asset
from .models.zipline_app.placement import Placement

from .widgets import AssetModelSelect2Widget, AccountModelSelect2Widget, ReadOnlyWidgetSimple, ReadOnlyWidgetAsset, ReadOnlyWidgetOrder, CustodianModelSelect2Widget, FillUnitWidget
from django import forms

# override widget in createview
# http://stackoverflow.com/a/21407374/4126114
# Override a Django generic class-based view widget
# http://stackoverflow.com/a/27322032/4126114
class FillForm(forms.ModelForm):
  source=forms.CharField(required=False, widget = forms.HiddenInput())
  field_order = [
    'pub_date', 'dedicated_to_order', 'fill_side', 'asset', 'fill_qty_unsigned', 'fill_unit',
    'fill_price', 'category', 'is_internal', 'trade_date', 'settlement_date',
    'custodian', 'fill_text'
  ]
  class Meta:
    model=Fill
    exclude = ["user"]
    widgets = {
      'pub_date': ReadOnlyWidgetSimple(),
      'dedicated_to_order': ReadOnlyWidgetOrder(),
      'custodian': CustodianModelSelect2Widget(),
      'asset': ReadOnlyWidgetAsset(),
      'fill_side': forms.HiddenInput(),
      'fill_unit': FillUnitWidget(),
    }
  def clean_pub_date(self): return self.initial['pub_date'] #.strftime("%Y-%m-%d %H:%i:%s")
  def clean_dedicated_to_order(self): return self.initial['dedicated_to_order']
  def clean_asset(self):
    aid = self.initial['asset']
    if not isinstance(aid, int): return aid
    return Asset.objects.get(id=aid)
  def clean_fill_side(self): return self.initial['fill_side']
  def clean_source(self): return self.initial['source'] if 'source' in self.initial else None
  def clean_fill_unit(self): return self.initial['fill_unit']

  def __init__(self, *args, **kwargs):
    super(FillForm, self).__init__(*args, **kwargs)
    self.fields['fill_unit'].widget.form_instance = self

class OrderForm(forms.ModelForm):
  source=forms.CharField(required=False, widget = forms.HiddenInput())
  field_order = [
    'id',
    'pub_date',
    'user',
    'order_side',
    'account',
    'asset',
    'order_unit',
    'order_qty_unsigned',

    # fields for tables.py
    'asset_currency',
    'order_amount',
    'order_qty',

    'am_type',
    'order_type',
    'limit_price',
    'order_validity',
    'validity_date',
    'order_text',
    'commission'
  ]

  class Meta:
    model=Order
    exclude=['user']
    widgets = {
      'pub_date': ReadOnlyWidgetSimple(),
      'asset': AssetModelSelect2Widget(),
      'account': AccountModelSelect2Widget(),
    }
  def clean_pub_date(self): return self.initial['pub_date'] #.strftime("%Y-%m-%d %H:%i:%s")
  def clean_source(self): return self.initial['source'] if 'source' in self.initial else None


class PlacementForm(forms.ModelForm):
  class Meta:
    model=Placement
    exclude = ["date", "user"]
