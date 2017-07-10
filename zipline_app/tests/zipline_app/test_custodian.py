from django.test import TestCase
from .test_zipline_app import create_custodian
from django.urls import reverse
from ...utils import myTestLogin

class CustodianViewsTests(TestCase):
  def setUp(self):
    myTestLogin(self.client)

  def test_list(self):
    url = reverse('zipline_app:custodians-list')
    response = self.client.get(url)
    self.assertEqual(response.status_code, 200)

  def test_new(self):
    url = reverse('zipline_app:custodians-new')
    response = self.client.get(url)
    self.assertEqual(response.status_code, 200)

  def test_delete_ok(self):
    c1 = create_custodian("C1", "c1")
    url = reverse('zipline_app:custodians-delete', args=(c1.id,))
    response = self.client.get(url)
    self.assertEqual(response.status_code, 200)

  def test_update(self):
    c1 = create_custodian("c1","c1")
    url = reverse('zipline_app:custodians-update', args=(c1.id,))
    response = self.client.get(url)
    self.assertEqual(response.status_code, 200)

class CustodianModelTests(TestCase):
  def test_create_delete(self):
    cust1 = create_custodian("C1", "Custodian 1")
    cust1.delete()
