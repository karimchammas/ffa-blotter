import datetime
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from ...models.zipline_app.order import Order, OrderManager
from .test_zipline_app import create_asset, create_order, create_account, a1
from ...models.zipline_app.fill import Fill
from ...models.zipline_app.side import BUY, SELL, MARKET, GTC, GTD, DAY, OPEN, CANCELLED
from .test_fill import create_fill_from_order, url_permission
from ...utils import myTestLogin
from django.contrib.auth.models import User
from django.core import mail

class OrderModelTests(TestCase):
    def setUp(self):
      self.acc1 = create_account(symbol="TEST01")
      self.a1a = create_asset(a1["symbol"],a1["exchange"],a1["name"])

    def test_buy(self):
        o1 = create_order(order_text="test?",days=-1, asset=self.a1a, order_side=BUY, order_qty_unsigned=10, account=self.acc1)

    def test_sell(self):
        o1 = create_order(order_text="test?",days=-1, asset=self.a1a, order_side=SELL, order_qty_unsigned=10, account=self.acc1)

    def test_signed(self):
        o1 = create_order(order_text="test?",days=-1, asset=self.a1a, order_side=BUY, order_qty_unsigned=10, account=self.acc1)
        self.assertEqual(o1.order_qty_signed(), 10)
        o1 = create_order(order_text="test?",days=-1, asset=self.a1a, order_side=SELL, order_qty_unsigned=10, account=self.acc1)
        self.assertEqual(o1.order_qty_signed(), -10)

    def test_dedicated_fill(self):
        o1 = create_order(order_text="test?",days=-1, asset=self.a1a, order_side=BUY, order_qty_unsigned=10, account=self.acc1)
        f1 = create_fill_from_order(order=o1, fill_text="fill text", fill_price=1)
        self.assertEqual(o1.dedicated_fill(), f1)

        # test that can now delete
        o1.delete()

    def test_order_with_user(self):
      password='bla'
      user = User.objects.create_user(username='john', email='jlennon@beatles.com', password=password)
      o1 = create_order(days=-1, asset=self.a1a, order_side=BUY, order_qty_unsigned=1, order_text="order 1", user=user, account=self.acc1)

    def test_history(self):
      o1 = create_order(order_text="test?",days=-1, asset=self.a1a, order_side=BUY, order_qty_unsigned=10, account=self.acc1)
      self.assertEqual(o1.history().count(), 0)
      o1.order_side=SELL
      o1.save()
      self.assertEqual(o1.history().count(), 1)

    def test_clean(self):
      order = create_order(order_text="random order", days=-1,  asset=self.a1a, order_side=BUY, order_qty_unsigned=10,   account=self.acc1)
      order.order_validity = GTD
      order.validity_date = timezone.now()
      order.clean()
      self.assertEqual(order.validity_date.hour, 23)

    def provider_validity(self, order_validity, validity_date, pub_date, user):
      order = Order.objects.create(
        order_text='test order',
        pub_date=pub_date,
        asset=self.a1a,
        order_side=BUY,
        order_qty_unsigned=10,
        account=self.acc1,
        user=user,
        order_validity=order_validity,
        validity_date=validity_date
      )
      order.refresh_from_db() # by the time the order is created, it could be cancelled
      order.clean()
      order.save()
      return order

    # assert that GTC order does not get instantly cancelled
    def test_validity_GTC(self):
      user = myTestLogin(self.client)
      order = self.provider_validity(order_validity=GTC, validity_date=None, pub_date=timezone.now(), user=user)
      order.refresh_from_db()
      self.assertEqual(order.order_status,OPEN)

    # assert that GTD order does not get instantly cancelled
    def test_validity_GTD(self):
      user = myTestLogin(self.client)
      order = self.provider_validity(order_validity=GTD, validity_date=timezone.now(), pub_date=timezone.now(), user=user)
      order.refresh_from_db()
      self.assertEqual(order.order_status,OPEN)

    # assert that DAY order does not get instantly cancelled
    def test_validity_DAY_new_then_old(self):
      user = myTestLogin(self.client)
      o1 = self.provider_validity(order_validity=DAY, validity_date=None, pub_date=timezone.now(), user=user)
      o2 = self.provider_validity(order_validity=DAY, validity_date=None, pub_date=timezone.now() + datetime.timedelta(days=-1), user=user)
      om = OrderManager()
      om.process()
      o1.refresh_from_db()
      o2.refresh_from_db()
      self.assertEqual(o2.order_status,CANCELLED)
      self.assertEqual(o1.order_status,OPEN)

    # https://docs.djangoproject.com/en/1.10/topics/testing/tools/#email-services
    def test_create_order_sends_email(self):
      user = myTestLogin(self.client)
      with self.settings(EMAIL_HOST="bla", EMAIL_PORT="dummy", EMAIL_HOST_USER="dummy", EMAIL_HOST_PASSWORD="dummy"):
        o1 = self.provider_validity(order_validity=DAY, validity_date=None, pub_date=timezone.now(), user=user)
        self.assertEqual(len(mail.outbox), 1)
        self.assertTrue("New order" in mail.outbox[0].subject)

class OrderGeneralViewsTests(TestCase):
    def setUp(self):
      self.acc1 = create_account(symbol="TEST01")
      self.a1a = create_asset(a1["symbol"],a1["exchange"],a1["name"])
      self.user = myTestLogin(self.client)

    def test_list(self):
        url = reverse('zipline_app:orders-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_new_get(self):
        url = reverse('zipline_app:orders-new')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_delete(self):
        o1 = create_order(order_text="test?",days=-1, asset=self.a1a, order_side=BUY, order_qty_unsigned=10, account=self.acc1, user=self.user)

        url = reverse('zipline_app:orders-delete', args=(self.a1a.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_new_post(self):
        # http://stackoverflow.com/questions/40005411/django-django-test-client-post-request
        time = '2015-01-01 00:00:00' #timezone.now() + datetime.timedelta(days=-0.5)
        url = reverse('zipline_app:orders-new')
        response = self.client.post(url, {'pub_date':time, 'asset':self.a1a.id, 'order_side': BUY, 'order_qty_unsigned':10, 'account':self.acc1.id, 'order_type': MARKET, 'order_validity': GTC})
        # check that the post was successful by being a redirect
        #self.assertNotContains(response, 'has-error')
        self.assertNotEqual(response.status_code, 200)
        self.assertEqual(response.status_code, 302)

#        print(response.context)
#        self.assertFormError(response, 'form', 'pub_date', 'Enter a valid date/time.')
        #self.assertFormError(response, 'form', 'asset', 'Enter a valid date/time.')
        #self.assertFormError(response, 'form', 'amount', 'Enter a valid date/time.')
        #self.assertFormError(response, 'form', 'account', 'Select a valid choice. That choice is not one of the available choices.')

    def test_quantity_large_does_not_trigger_error_integer_too_large(self):
        time = '2015-01-01 00:00:00' #timezone.now() + datetime.timedelta(days=-0.5)
        url = reverse('zipline_app:orders-new')
        largeqty=100000000000000000000000000000
        response = self.client.post(url, {'pub_date':time, 'asset':self.a1a.id, 'order_side': BUY, 'order_qty_unsigned':largeqty, 'account':self.acc1.id})
        self.assertContains(response,"Ensure this value is less than or equal to")

    def test_new_order_timezone(self):
        url = reverse('zipline_app:orders-new')
        time = '2015-01-01 06:00:00'
        o1={'pub_date':time, 'asset':self.a1a.id, 'order_side': BUY, 'order_qty_unsigned':1, 'account':self.acc1.id}
        response = self.client.post(url,o1,follow=True)
        self.assertContains(response,"06:00")

    def test_new_order_zeroqty(self):
        url = reverse('zipline_app:orders-new')
        time = '2015-01-01 06:00:00'
        o1={'pub_date':time, 'asset':self.a1a.id, 'order_side': BUY, 'order_qty_unsigned':0, 'account':self.acc1.id}
        response = self.client.post(url,o1)
        self.assertContains(response,"Quantity 0 is not allowed")

    def test_new_order_user(self):
        url = reverse('zipline_app:orders-new')
        time = '2015-01-01 06:00:00'
        o1={'pub_date':time, 'asset':self.a1a.id, 'order_side': BUY, 'order_qty_unsigned':1, 'account':self.acc1.id, 'order_type': MARKET, 'order_validity': GTC}

        response = self.client.post(url,o1,follow=True)
        # check that "john" shows up twice, once for the "logged in as john", and once for the order author
        self.assertEqual(b''.join(list(response)).count(b"john"),2)

class OrderDetailViewTests(TestCase):
    def setUp(self):
      self.acc1 = create_account(symbol="TEST01")
      self.a1a = create_asset(a1["symbol"],a1["exchange"],a1["name"])
      self.user = myTestLogin(self.client)

    def test_detail_view_with_a_future_order(self):
        """
        The detail view of a order with a pub_date in the future should
        return a 404 not found.
        """
        future_order = create_order(order_text='Future order.', days=5, asset=self.a1a, order_side=BUY, order_qty_unsigned=10, account=self.acc1)
        url = reverse('zipline_app:orders-detail', args=(future_order.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_detail_view_with_a_past_order(self):
        """
        The detail view of a order with a pub_date in the past should
        display the order's text.
        """
        past_order = create_order(order_text='Past Order.', days=-5, asset=self.a1a, order_side=BUY, order_qty_unsigned=10, account=self.acc1)
        url = reverse('zipline_app:orders-detail', args=(past_order.id,))
        response = self.client.get(url)
        self.assertContains(response, past_order.order_text)

    def test_update(self):
        o1 = create_order(order_text="test?",days=-1, asset=self.a1a, order_side=BUY, order_qty_unsigned=10, account=self.acc1, user=self.user)

        url = reverse('zipline_app:orders-update', args=(self.a1a.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_detail_view_history(self):
      order = create_order(order_text='original order.', days=-5, asset=self.a1a, order_side=BUY, order_qty_unsigned=10, account=self.acc1)
      url = reverse('zipline_app:orders-detail', args=(order.id,))
      response = self.client.get(url, follow=True)
      self.assertContains(response, "No history")
      order.order_side=SELL
      order.save()
      response = self.client.get(url, follow=True)
      self.assertContains(response, "Changed order_side from")

    def test_detail_edit_del_only_for_owner(self):
      o1 = create_order(order_text="test", days=-10, asset=self.a1a, order_side=BUY, order_qty_unsigned=10, account=self.acc1, user=self.user)

      url = reverse('zipline_app:orders-detail', args=(o1.id,))

      response = self.client.get(url, follow=True)
      self.assertContains(response, "Edit")
      self.assertContains(response, "Delete")

      password='bla'
      u2 = User.objects.create_user(username='ringo', email='ringo@beatles.com', password=password)
      self.client.logout()
      self.client.login(username=u2.username, password=password)
      self.assertEqual(response.status_code, 200)

      response = self.client.get(url, follow=True)
      self.assertNotContains(response, "Edit")
      self.assertNotContains(response, "Delete")


    def test_edit_only_for_owner(self):
      o1 = create_order(order_text="test", days=-10, asset=self.a1a, order_side=BUY, order_qty_unsigned=10, account=self.acc1, user=self.user)
      url_permission(self, 'zipline_app:orders-update', o1.id)

    def test_del_only_for_owner(self):
      o1 = create_order(order_text="test", days=-10, asset=self.a1a, order_side=BUY, order_qty_unsigned=10, account=self.acc1, user=self.user)
      url_permission(self, 'zipline_app:orders-delete', o1.id)
