from .models.zipline_app.asset import Asset
from .models.zipline_app.account import Account
from .models.zipline_app.order import Order, ORDER_UNIT_CHOICES, SHARE
from .models.zipline_app.custodian import Custodian

# using select2, copied from https://github.com/applegrew/django-select2/blob/master/tests/testapp/forms.py
from django_select2.forms import ModelSelect2Widget
from django.utils.encoding import force_text

from django.forms import widgets

class AssetModelSelect2Widget(ModelSelect2Widget):
    model = Asset
    search_fields = [
        'asset_name__icontains',
        'asset_symbol__icontains',
        'asset_origin__icontains'
    ]
    def label_from_instance(self, obj):
      return force_text(obj.__str__())

class AccountModelSelect2Widget(ModelSelect2Widget):
    model = Account
    search_fields = [
        'account_name__icontains',
        'account_symbol__icontains',
        'account_origin__icontains'
    ]
    def label_from_instance(self, obj):
      return force_text(obj.__str__())

class CustodianModelSelect2Widget(ModelSelect2Widget):
    model = Custodian
    search_fields = [
        'custodian_name__icontains',
        'custodian_symbol__icontains',
        'custodian_origin__icontains'
    ]
    def label_from_instance(self, obj):
      return force_text(obj.__str__())

# PUBLISHED here: https://gist.github.com/shadiakiki1986/e27edd06f2cb3ad4110405235849ebfb
#
# In a Django form, how do I make a field readonly (or disabled) so that it cannot be edited?
# https://stackoverflow.com/a/15134622/4126114
#
# Modifications (not published to gist):
# Replace widgets.Widget with widgets.TextInput
#    This allows appending the <p>...</p> while maintain an input to the post
# Replace type="text" with type="hidden" manually
#    This allows for the label to be generated automatically
class ReadOnlyWidgetSimple(widgets.TextInput):
  """Some of these values are read only - just a bit of text..."""
  def render(self, name, value, attrs=None):
    out = super().render(name, value, attrs)
    p1 = "<p>"+str(value)+"</p>"
    out = out.replace("text", "hidden")
    return out + p1

from django.urls import  reverse
class ReadOnlyWidgetModel(widgets.TextInput):
  model = None
  """Some of these values are read only - just a bit of text..."""
  def render(self, name, value, attrs=None):
    if not value: return super().render(name, "N/A", attrs)
    if not self.model: raise Exception("Define model")
    if not self.url_detail: raise Exception("Define url_detail")

    out = super().render(name, value, attrs)
    out = out.replace("text", "hidden")

    url = reverse(self.url_detail, args=(value,))
    p1 = "<a href='"+url+"'>#"+str(value)+"</a>"
    return out+"<span>"+p1+"</span>"

class ReadOnlyWidgetAsset(ReadOnlyWidgetModel):
  model = Asset
  url_detail = 'zipline_app:assets-detail'
  def render(self, name, value, attrs=None):
    out = super().render(name, value, attrs)
    asset = self.model.objects.get(id=value)
    append = ": "+str(asset)
    return "<p>"+out + append+"</p>"

class ReadOnlyWidgetOrder(ReadOnlyWidgetModel):
  model = Order
  url_detail = 'zipline_app:orders-detail'
  def render(self, name, value, attrs=None):
    order_link = super().render(name, value, attrs)
    order = self.model.objects.get(id=value)
    url = reverse('zipline_app:assets-detail', args=(order.account.id,))
    account_link = "<a href='"+url+"'>"+order.account.account_symbol+"</a>"

    out = "<p>%s: %s %s %s for %s</p>" % (
      order_link,
      order.get_order_side_display(),
      str(order.order_qty_unsigned),
      order.get_order_unit_display(),
      account_link
    )
    return out

class FillUnitWidget(widgets.TextInput):
  def render(self, name, value, attrs=None):
    out = super().render(name, value, attrs)
    out = out.replace("text", "hidden")

    value2 = ""
    if value==ORDER_UNIT_CHOICES[0][0]:
      value2 = ORDER_UNIT_CHOICES[0][1]
    else:
      value2 = ORDER_UNIT_CHOICES[1][1]

    if value==SHARE:
      return out + "<p>"+value2+"</p>"

    order_id = self.form_instance.initial['dedicated_to_order']
    order = Order.objects.get(id=order_id)
    currency = order.asset.asset_currency
    return out + "<p>"+value2+"&nbsp;("+currency+")</p>"
