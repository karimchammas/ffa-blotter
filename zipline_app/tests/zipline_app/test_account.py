from .test_zipline_app import OrderBaseTests
from django.urls import reverse
from ...utils import myTestLogin
from ...models.zipline_app.side import BUY

class AccountViewsTests(OrderBaseTests):
    def test_list(self):
        url = reverse('zipline_app:accounts-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_new(self):
        url = reverse('zipline_app:accounts-new')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_delete_ok(self):
        url = reverse('zipline_app:accounts-delete', args=(self.a1a.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_update(self):
        url = reverse('zipline_app:accounts-update', args=(self.a1a.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

class AccountModelTests(OrderBaseTests):
  def test_delete_fail(self):
    o1 = self.create_order_default(account=self.acc1)
    with self.assertRaises(ValueError):
      self.acc1.delete()
