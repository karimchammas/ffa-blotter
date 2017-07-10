from .models.zipline_app.asset import Asset
from .models.zipline_app.account import Account
from .models.zipline_app.order import Order
from .models.zipline_app.custodian import Custodian

# using select2, copied from https://github.com/applegrew/django-select2/blob/master/tests/testapp/forms.py
from django_select2.forms import ModelSelect2Widget
from django.utils.encoding import force_text

from django.forms import widgets

class AssetModelSelect2Widget(ModelSelect2Widget):
    model = Asset
    search_fields = [
        'asset_name__icontains',
        'asset_symbol__startswith'
    ]
    def label_from_instance(self, obj):
      return force_text(obj.__str__())

class AccountModelSelect2Widget(ModelSelect2Widget):
    model = Account
    search_fields = [
        'account_name__icontains',
        'account_symbol__startswith'
    ]
    def label_from_instance(self, obj):
      return force_text(obj.__str__())

class CustodianModelSelect2Widget(ModelSelect2Widget):
    model = Custodian
    search_fields = [
        'custodian_name__icontains',
        'custodian_symbol__startswith'
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

    p2 = ""
    if self.show_str:
      p2 = self.model.objects.get(id=value)
      p2 = ": "+str(p2)

    return out + "<p>"+p1+p2+"</p>"


    return v3

class ReadOnlyWidgetAsset(ReadOnlyWidgetModel):
  model = Asset
  url_detail = 'zipline_app:assets-detail'
  show_str=True

class ReadOnlyWidgetOrder(ReadOnlyWidgetModel):
  model = Order
  url_detail = 'zipline_app:orders-detail'
  show_str=False

#########################
from .models.zipline_app.side import FILL_SIDE_CHOICES
class ReadOnlyWidgetOrderSide(ReadOnlyWidgetSimple):
  def render(self, name, value, attrs=None):
    if not value: return super().render(name, "N/A", attrs)
    filtered = [x for x in FILL_SIDE_CHOICES if x[0]==value]
    v2 = filtered[0][1]
    v3 = super().render(name, v2, attrs)
    v3 = v3.replace('value="'+v2+'"', 'value="'+str(value)+'"')
    return v3

class OrderQtyUnitWidget(widgets.TextInput):
  def render(self, name, value, attrs=None):
    # original = super().render("order_qty_unit", "shares", attrs)
    if value is None: value="shares"
    out = super().render(name, value, attrs)
    out = out.replace("text", "radio")
    out = out.replace("input", "input checked")
    out = out.replace("form-control","")
    out = "<label>"+out+"&nbsp;"+value+"&nbsp;&nbsp;</label>"
    out2 = ""
    if value!="shares":
      out2 = out
      out2 = out2.replace(value,"shares")
      out2 = out2.replace(" checked","")
    return out2+out
