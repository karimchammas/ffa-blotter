from django.test import TestCase
from django.urls import reverse
from ...models.zipline_app.fill import Fill
from ...models.zipline_app.side import BUY, SELL, DAY
from .test_fill import FillBaseTests
from ...utils import myTestLogin, chopSeconds
from django.utils import timezone
import datetime
from ...models.zipline_app.order import Order, OrderManager

class BlotterConcealedViewsTests(FillBaseTests):
  def test_one_order(self):
    order = self.create_order_default(order_text="random order")
    f1 = self.create_fill_from_order_default(order=order, fill_text="test fill", fill_price=2)

    url = reverse('zipline_app:blotter-concealed')
    response = self.client.get(url, follow=True)
    self.assertContains(response, "random order")
    self.assertNotContains(response, "test fill")

    self.assertContains(response, "Fill") # used to be "Filled by"

  def test_two_orders_different(self):
    o_l = self.create_order_default(order_text="buy order", order_side=BUY)
    o_s = self.create_order_default(order_text="sell order", order_side=SELL, order_qty_unsigned=20)
    f_l = self.create_fill_from_order_default(order=o_l, fill_text="test fill buy", fill_price=2)
    f_s = self.create_fill_from_order_default(order=o_s, fill_text="test fill sell", fill_price=2)

    url = reverse('zipline_app:blotter-concealed')
    response = self.client.get(url, follow=True)
    self.assertContains(response, "buy order")
    self.assertContains(response, "sell order")
    self.assertNotContains(response, "test fill buy")
    self.assertNotContains(response, "test fill sell")

  def test_no_fill_create_button(self):
    url = reverse('zipline_app:blotter-concealed')
    response = self.client.get(url, follow=True)
    self.assertNotContains(response, 'data-target="#fills-new"')

  def test_day_order_expires(self):
    past = timezone.now() + datetime.timedelta(days=-1)
    past = chopSeconds(past)
    order = Order.objects.create(
      order_text='test order',
      pub_date=past,
      asset=self.a1a,
      order_side=BUY,
      order_qty_unsigned=10,
      account=self.acc1,
      order_validity=DAY
    )
    order.clean()
    order.save()

    url = reverse('zipline_app:blotter-concealed')
    response = self.client.get(url, follow=True)
    self.assertContains(response, "test order")
    self.assertContains(response, "Cancelled")

  def test_sorting_filtering_shows_note_on_top(self):
    o_l = self.create_order_default(order_text="buy order")

    url = reverse('zipline_app:blotter-concealed')
    response = self.client.get(url, follow=True)
    self.assertNotContains(response, "Sorted by")

    url = reverse('zipline_app:blotter-concealed')+'?sort=account__account_name'
    response = self.client.get(url, follow=True)
    self.assertContains(response, "Sorted by")
