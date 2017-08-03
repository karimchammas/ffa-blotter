from django.test import TestCase
from .test_zipline_app import OrderBaseTests
from django.urls import reverse
from ...utils import myTestLogin
from ...models.zipline_app.side import BUY

class AssetViewsTests(OrderBaseTests):
    def test_list(self):
        url = reverse('zipline_app:assets-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_new(self):
        url = reverse('zipline_app:assets-new')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_delete(self):
        url = reverse('zipline_app:assets-delete', args=(self.a1a.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_update(self):
        url = reverse('zipline_app:assets-update', args=(self.a1a.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)


class AssetModelTests(OrderBaseTests):
  # cannot delete asset linked to order
  def test_delete_fail(self):
    o1 = self.create_order_default()
    with self.assertRaises(ValueError):
      self.a1a.delete()
