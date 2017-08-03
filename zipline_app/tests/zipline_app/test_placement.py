from django.test import TestCase
from ...models.zipline_app.placement import Placement
from .test_zipline_app import create_a1, create_account, a1, create_order
from ...models.zipline_app.side import BUY
from ...utils import myTestLogin
from django.core import mail
from django.urls import reverse

class PlacementBaseTests(TestCase):
  def setUp(self):
    acc1 = create_account(symbol="TEST01")
    a1a = create_a1()
    self.user = myTestLogin(self.client)
    self.o1 = create_order(order_text="test?",days=-1, asset=a1a, order_side=BUY, order_qty_unsigned=10, account=acc1, user=self.user)

class PlacementModelTests(PlacementBaseTests):
  def test_create(self):
    Placement.objects.create(order=self.o1, user=self.user)
    self.assertEqual(len(mail.outbox), 2)
    self.assertTrue("New order" in mail.outbox[0].subject)
    self.assertTrue("Placement for order" in mail.outbox[1].subject)

class PlacementCreateViewTests(PlacementBaseTests):
  def test_new(self):
    url = reverse('zipline_app:orders-new')
    response = self.client.post(url, {'order': self.o1.id})
    self.assertEqual(response.status_code, 200)

