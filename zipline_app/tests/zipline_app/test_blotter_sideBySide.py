from django.test import TestCase
from .test_zipline_app import OrderBaseTests
from django.urls import reverse
from ...models.zipline_app.fill import Fill
from ...models.zipline_app.side import BUY, SELL
from ...utils import myTestLogin

class BlotterSideBySideViewsTests(OrderBaseTests):
  def test_one_order(self):
    order = self.create_order_default(order_text="random order")
    url = reverse('zipline_app:blotter-sideBySide')
    response = self.client.get(url, follow=True)
    self.assertContains(response, "random order")

  def test_two_orders(self):
    o_l = self.create_order_default(order_text="buy order", order_side=BUY)
    o_s = self.create_order_default(order_text="sell order", order_side=SELL)

    url = reverse('zipline_app:blotter-sideBySide')
    response = self.client.get(url, follow=True)
    self.assertContains(response, "buy order")
    self.assertContains(response, "sell order")
