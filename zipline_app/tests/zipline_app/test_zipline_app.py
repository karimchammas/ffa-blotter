import datetime
from django.utils import timezone
from django.test import TestCase
from django.urls import reverse
from time import sleep
import pandas as pd
from unittest import skip
from ...models.zipline_app.zipline_app import Order, Fill, Account, Asset
from ...models.zipline_app.custodian import Custodian
from ...models.zipline_app.side import BUY
from ...utils import myTestLogin, chopSeconds

a1 = {
  "exchange":'exchange name',
  "symbol":'A1',
  "name":'A1 name',
  "currency": 'USD',
  "isin": None,
  "origin": "Manual"
}
a2 = {
  "exchange":'exchange name',
  "symbol":'A2',
  "name":'A2 name',
  "currency": 'USD',
  "isin": None,
  "origin": "Manual"
}

def create_account(symbol):
    return Account.objects.create(
      account_symbol=symbol
    )

def create_asset(symbol, exchange, name, currency):
    return Asset.objects.create(
      asset_exchange=exchange,
      asset_symbol=symbol,
      asset_name=name,
      asset_currency = currency
    )

def create_a1(): return create_asset(a1["symbol"],a1["exchange"],a1["name"],a1["currency"])

def create_order(order_text, days, asset, order_side, order_qty_unsigned, account, user, *args, **kwargs):
    """
    Creates a order with the given `order_text` and published the
    given number of `days` offset to now (negative for orders published
    in the past, positive for orders that have yet to be published).
    """
    time = timezone.now() + datetime.timedelta(days=days)
    time = chopSeconds(time)
    order = Order.objects.create(
      order_text=order_text,
      pub_date=time,
      asset=asset,
      order_side=order_side,
      order_qty_unsigned=order_qty_unsigned,
      account=account,
      user=user,
      *args,
      **kwargs
    )
    order.full_clean()
    order.save()
    return order

def create_fill(fill_text, days, asset, fill_side, fill_qty_unsigned, fill_price, tt_order_key="", dedicated_to_order=None, user=None, custodian=None):
    if dedicated_to_order is None:
      raise Exception("As of 2017-06-29, cannot create fill without assigning it to an order anymore")
    time = timezone.now() + datetime.timedelta(days=days)
    fill = Fill.objects.create(
      fill_text=fill_text, pub_date=time, asset=asset,
      fill_side=fill_side, fill_qty_unsigned=fill_qty_unsigned, fill_price=fill_price,
      tt_order_key=tt_order_key,
      dedicated_to_order=dedicated_to_order,
      user=user,
      custodian=custodian
    )
    fill.full_clean()
    fill.save()
    return fill

def create_fill_from_order(order, fill_text, fill_price, tt_order_key, user, custodian):
    fill = Fill.objects.create(
      fill_text=fill_text,
      pub_date=order.pub_date,
      asset=order.asset,
      fill_side=order.order_side,
      fill_qty_unsigned=order.order_qty_unsigned,
      fill_price=fill_price,
      tt_order_key=tt_order_key,
      dedicated_to_order=order,
      user=user,
      custodian=custodian
    )
    fill.full_clean()
    fill.save()
    return fill

def create_custodian(symbol, name):
  return Custodian.objects.create(custodian_symbol=symbol, custodian_name=name)

class OrderBaseTests(TestCase):
    def setUp(self):
      self.acc1 = create_account(symbol="TEST01")
      self.a1a = create_a1()
      self.user = myTestLogin(self.client)

    def create_order_default(self, order_text=None, days=None, asset=None, order_side=None, order_qty_unsigned=None, account=None, user=None, commission=None):
      order_text = "test?" if order_text is None else order_text
      days = -1 if days is None else days
      asset = self.a1a if asset is None else asset
      order_side = BUY if order_side is None else order_side
      order_qty_unsigned = 10 if order_qty_unsigned is None else order_qty_unsigned
      account = self.acc1 if account is None else account
      user = self.user if user is None else user
      return create_order(
        order_text=order_text,days=days, asset=asset, order_side=order_side, order_qty_unsigned=order_qty_unsigned, account=account, user=user,
        commission=commission # Note that commission=None is allowed
      )

class OrderMethodTests(OrderBaseTests):
    def setUp(self):
      super(OrderMethodTests, self).setUp()
      self.a2a = create_asset(a2["symbol"],a2["exchange"],a2["name"],a2["currency"])

    def test_was_published_recently_with_future_order(self):
        """
        was_published_recently() should return False for orders whose
        pub_date is in the future.
        """
        future_order = self.create_order_default(days=30)
        self.assertIs(future_order.was_published_recently(), False)

    def test_was_published_recently_with_old_order(self):
        """
        was_published_recently() should return False for orders whose
        pub_date is older than 1 day.
        """
        old_order = self.create_order_default(days=-30)
        self.assertIs(old_order.was_published_recently(), False)

    def test_was_published_recently_with_recent_order(self):
        """
        was_published_recently() should return True for orders whose
        pub_date is within the last day.
        """
        recent_order = self.create_order_default(days=-0.5)
        self.assertIs(recent_order.was_published_recently(), True)

    def test_avg_price(self):
        o = self.create_order_default(days=-0.5)
        cust = create_custodian("c1", "c1 name")
        f = create_fill_from_order(o, "test", 1, tt_order_key="", user=self.user, custodian=cust)
        self.assertEqual(o.avgPrice(), 1)

    def test_asset_to_dict(self):
        o = self.create_order_default(days=-0.5)
        self.assertEqual(o.asset.to_dict(), a1)

class OrderViewTests(OrderBaseTests):
    def test_blotter_concealed_view_with_no_orders(self):
        """
        If no orders exist, an appropriate message should be displayed.
        """
        response = self.client.get(reverse('zipline_app:orders-list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No orders are available.")
        self.assertQuerysetEqual(response.context['latest_order_list'], [])
        # 2017-07-08: cannot create fills directly, but only via order
        # self.assertContains(response, "New fill")

    def test_blotter_concealed_view_with_a_past_order(self):
        """
        Orders with a pub_date in the past should be displayed on the
        blotter_engine page.
        """
        self.create_order_default(order_text="Past order.", days=-30)
        response = self.client.get(reverse('zipline_app:orders-list'))
        self.assertQuerysetEqual(
            response.context['latest_order_list'],
            ['<Order: A1, B, 10.0 (TEST01, Past order.)>']
        )

    def test_blotter_concealed_view_with_a_future_order(self):
        """
        Orders with a pub_date in the future should not be displayed on
        the blotter_engine page.
        """
        self.create_order_default(order_text="Future order.", days=30)
        response = self.client.get(reverse('zipline_app:orders-list'))
        self.assertContains(response, "No orders are available.")
        self.assertQuerysetEqual(response.context['latest_order_list'], [])

    def test_blotter_concealed_view_with_future_order_and_past_order(self):
        """
        Even if both past and future orders exist, only past orders
        should be displayed.
        """
        self.create_order_default(order_text="Past order.", days=-30)
        self.create_order_default(order_text="Future order.", days=30)
        response = self.client.get(reverse('zipline_app:orders-list'))
        self.assertQuerysetEqual(
            response.context['latest_order_list'],
            ['<Order: A1, B, 10.0 (TEST01, Past order.)>']
        )

    def test_blotter_concealed_view_with_two_past_orders(self):
        """
        The orders blotter_engine page may display multiple orders.
        """
        self.create_order_default(order_text="Past order 1.", days=-30)
        self.create_order_default(order_text="Past order 2.", days=-5)
        response = self.client.get(reverse('zipline_app:orders-list'))
        self.assertQuerysetEqual(
            response.context['latest_order_list'],
            ['<Order: A1, B, 10.0 (TEST01, Past order 2.)>', '<Order: A1, B, 10.0 (TEST01, Past order 1.)>']
        )

    def test_index_view_combined_general(self):
        """
        This test sometimes fails and then passes when re-run
        .. not sure why yet
        .. seems to be solved by sleep 50 ms
        """
        o1 = self.create_order_default(order_text="Past order 1.", days=-30)
        o2 = self.create_order_default(order_text="Past order 2.", days=-5)
        cust = create_custodian("c1", "c1 name")
        f1 = create_fill_from_order(order=o1, fill_text="test?", fill_price=2, tt_order_key="", user=self.user, custodian=cust)
        f2 = create_fill_from_order(order=o2, fill_text="test?", fill_price=2, tt_order_key="", user=self.user, custodian=cust)
        sleep(0.05)
        response = self.client.get(reverse('zipline_app:orders-list'))

        pointer = response.context['combined'][1]
        self.assertEqual(
            pointer["minute"],
            pd.Timestamp(o1.pub_date,tz='utc').floor('1Min')
        )

        pointer = pointer["duos"][0]
        self.assertEqual(
          pointer["asset"],
          o1.asset
        )

        self.assertQuerysetEqual(
            pointer['orders'],
            [
              '<Order: A1, B, 10.0 (TEST01, Past order 1.)>',
            ]
        )
        self.assertQuerysetEqual(
            pointer['fills'],
            [
              '<Fill: A1, B 10.0, 2.0 (, test?) - dedicated to A1, B, 10.0 (TEST01, Past order 1.)>',
            ]
        )

    def test_index_view_deleted_order_implies_deleted_minute(self):
        # be careful that with days=0 this test will fail
        # but not because the minute is showing up
        # but because the default field for order pub_date is also timezone.now()
        o1a = self.create_order_default(days=-10)
        cust = create_custodian("c1", "c1 name")
        f1 = create_fill_from_order(order=o1a, fill_text="test?", fill_price=2, tt_order_key="", user=self.user, custodian=cust)
        o1b = self.create_order_default(days=-9)

        time = o1b.pub_date
        sleep(0.05)
        response = self.client.get(reverse('zipline_app:orders-list'))
        self.assertContains(response, time.strftime("%Y-%m-%d"))

        o1b.delete()
        sleep(0.05)
        response = self.client.get(reverse('zipline_app:orders-list'))
        self.assertNotContains(response, time.strftime("%Y-%m-%d"))

    @skip("This test is not capturing the messages queue for some reason, and I couldnt get it to work")
    def test_index_view_create_delete_order_toggle_django_message(self):
        time = timezone.now()
        url = reverse('zipline_app:orders-new')
        o1 = {'pub_date':time, 'asset':self.a1a.id, 'order_side': BUY, 'order_qty_unsigned':10, 'account':self.acc1.id}
        response = self.client.post(url,o1,follow=True)

        messages = list(response.context['messages'])
        self.assertContains(messages[0],"Successfully created order")
#        o1.delete()
#        get_assert_contains(self,"Successfully deleted order")
#
#        f1 = create_fill(fill_text="test?",days=-30, asset=self.a1a, fill_side=BUY, fill_qty_unsigned=20, fill_price=2)
#        get_assert_contains(self,"Successfully created fill")
#        f1.delete()
#        get_assert_contains(self,"Successfully deleted fill")
#
#        as1=create_asset("test","test","test","test")
#        get_assert_contains(self,"Successfully created asset")
#
#        ac1=create_account("test")
#        get_assert_contains(self,"Successfully created account")

    def test_fills_required_per_asset(self):
        o1 = self.create_order_default(days=-10, order_qty_unsigned=5)
        o2 = self.create_order_default(days=-10, order_qty_unsigned=5)
        sleep(0.05)
        response = self.client.get(reverse('zipline_app:orders-list'))
        self.assertEqual(response.context['fills_required_per_asset'], {self.a1a:10})
        self.assertContains(response, "Assets with required fills")
        self.assertContains(response, self.a1a.asset_symbol+": 10")

        cust = create_custodian("c1", "c1 name")
        f1 = create_fill_from_order(order=o1, fill_text="test?", fill_price=2, tt_order_key="", user=self.user, custodian=cust)
        response = self.client.get(reverse('zipline_app:orders-list'))
        self.assertEqual(response.context['fills_required_per_asset'], {self.a1a:5})

        f2 = create_fill_from_order(order=o2, fill_text="test?", fill_price=2, tt_order_key="", user=self.user, custodian=cust)
        response = self.client.get(reverse('zipline_app:orders-list'))
        self.assertEqual(response.context['fills_required_per_asset'], {})
        self.assertNotContains(response, "Assets with required fills")
