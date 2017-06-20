# Create your views here.

from django.views import generic
from django.utils import timezone
from django.contrib import messages
from pandas import Timedelta
from numpy import concatenate

from ...models.zipline_app.order import Order
from ...models.zipline_app.fill import Fill
from ...models.zipline_app.asset import Asset
from ...models.zipline_app.account import Account
from ...models.zipline_app.side import OPEN

from .order import OrderCreate
from .fill import FillCreate
from .asset import AssetCreate
from .account import AccountCreate
from ._download_builder import DownloadBuilder

class BlotterBaseView(generic.ListView):
    context_object_name = 'latest_order_list'

    def get_queryset(self):
        """Return orders"""
        return self.get_orders()

    def get_context_data(self, *args, **kwargs):
        context = super(BlotterBaseView, self).get_context_data(*args, **kwargs)

        # append fills
        context['latest_fill_list'] = self.get_fills()

        # append forms
        # https://github.com/django/django/blob/feac4c30ce7635e17ce1adc4c2c7a1eb0721aeb3/django/views/generic/edit.py#L124
        form = OrderCreate()
        context["order_form"]=form.get_form_class()
        form = FillCreate()
        context["fill_form"]=form.get_form_class()
        form = AssetCreate()
        context["asset_form"]=form.get_form_class()
        form = AccountCreate()
        context["account_form"]=form.get_form_class()

        # append source for redirection
        context["source"]=self.source

        # alerts
        context["fills_required_per_asset"]=self.fills_required_per_asset()

        return context

    def get_sort(self):
      return self.request.GET.get("sort", "-pub_date")

    def order_by(self, queryset):
      return queryset.order_by(self.get_sort())

    def get_filter_account(self):
      return self.request.GET.get("account", None)

    def get_filter_asset(self):
      return self.request.GET.get("asset", None)

    def filter_account(self, queryset):
      account = self.get_filter_account()
      if account is not None:
        queryset = queryset.filter(account__id=account)
      return queryset

    def filter_asset(self, queryset):
      asset = self.get_filter_asset()
      if asset is not None:
        queryset = queryset.filter(asset__id=asset)
      return queryset

    def get_orders(self):
      return self.filter_asset(
               self.filter_account(
                 self.order_by(
                   Order.objects.filter(
                     pub_date__lte=timezone.now()
                   )
                 )
               )
             )

    def get_fills(self):
      return Fill.objects.filter(
          pub_date__lte=timezone.now()
      )#[:5]

    def fills_required_per_asset(self):
      fills = {}
      for order in self.get_orders():
        if order.filled()!=order.order_qty_signed():
          if order.asset not in fills: fills[order.asset]=0
          fills[order.asset]+=order.order_qty_signed() - order.filled()
      return fills

class BlotterSideBySideView(BlotterBaseView):
    template_name = 'zipline_app/blotter/sideBySide/index.html'
    source="blotter-sideBySide"

    def get_combined(self):
        all_min_zl = []
        all_min_orders = self.get_orders().all()
        all_min_orders = [x.pub_date for x in all_min_orders]
        all_min_zl.extend(all_min_orders)
        all_min_fills = self.get_fills().exclude(dedicated_to_order=None)
        all_min_fills = [x.pub_date for x in all_min_fills]
        all_min_zl.extend(all_min_fills)
        all_min_zl = list(set(all_min_zl))

        combined = []

        for minute in sorted(all_min_zl, reverse=True):
          minuteP1 = minute + Timedelta(minutes=1)
          orders = self.get_orders()
          orders = orders.filter(
            pub_date__gte=minute,
            pub_date__lt =minuteP1
          )
          fills = self.get_fills()
          fills = fills.filter(
            pub_date__gte=minute,
            pub_date__lt =minuteP1,
          )
          sids_orders = [o.asset.id for o in orders]
          sids_fills  = [f.asset.id for f in fills]
          sids = concatenate((sids_orders,sids_fills))
          sids = sorted(list(set(sids)))
          duos=[]
          for sid in sids:
            asset = Asset.objects.get(id=sid)
            asset_fills = fills.filter(asset=asset)
            asset_orders = orders.filter(asset=asset)
            duos.append({
              "asset": asset,
              "colspan": max(len(asset_orders),len(asset_fills)),
              "orders": asset_orders,
              "fills": asset_fills
            })

          combined.append({
            "minute":minute,
            "duos":duos
          })
        return combined

    def get_context_data(self, *args, **kwargs):
        context = super(BlotterSideBySideView, self).get_context_data(*args, **kwargs)
        context["combined"] = self.get_combined()
        return context

class BlotterConcealedView(BlotterBaseView):
    template_name = 'zipline_app/blotter/concealed/index.html'
    source="blotter-concealed"
    def get_context_data(self, *args, **kwargs):
        context = super(BlotterConcealedView, self).get_context_data(*args, **kwargs)
        context["sort"] = self.get_sort()

        filter_account = self.get_filter_account()
        if filter_account is not None:
          context["filter_account"] = Account.objects.get(id=self.get_filter_account())

        filter_asset = self.get_filter_asset()
        if filter_asset is not None:
          context["filter_asset"] = Asset.objects.get(id=self.get_filter_asset())

        c1 = ( context['sort'] is not None and context['sort'] != '-pub_date' )
        context['anyFilterOrSort'] = c1 or filter_account is not None or filter_asset is not None

        return context

class BlotterDownloadView(BlotterBaseView):
  def get(self, *args, **kwargs):
    orders = self.get_orders()
    builder = DownloadBuilder()
    df = builder.orders2df(orders)
    full_name = builder.df2xlsx(df)
    response = builder.fn2response(full_name)
    return response
