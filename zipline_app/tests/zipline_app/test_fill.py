from django.test import TestCase
from .test_zipline_app import create_fill, create_asset, create_a1, create_order, create_account, a2, create_fill_from_order, create_custodian, OrderBaseTests
from django.urls import reverse
from ...models.zipline_app.fill import Fill
from ...models.zipline_app.side import BUY, SELL, PRINCIPAL
from django.core.exceptions import ValidationError
from ...utils import myTestLogin
from django.contrib.auth.models import User
from django.utils.timezone import get_current_timezone
from django.core import mail
from ...models.zipline_app.order import Order, SHARE

class FillBaseTests(OrderBaseTests):
  def setUp(self):
    super(FillBaseTests, self).setUp()
    self.o1 = self.create_order_default()
    self.cust = create_custodian("C1","custodian name 1")

  def create_fill_from_order_default(self, order=None, fill_text=None, fill_price=None, user=None, tt_order_key=None, custodian=None):
    if order is None: order = self.o1
    if fill_text is None: fill_text = "test fill"
    if fill_price is None: fill_price = 2
    if user is None: user=self.user
    if tt_order_key is None: tt_order_key = "test key"
    if custodian is None: custodian = self.cust
    return create_fill_from_order(order=order, fill_text=fill_text, fill_price=fill_price, user=user, tt_order_key=tt_order_key, custodian=custodian)

class FillModelTests(FillBaseTests):
  def test_clean_invalid_dedicated_order_qty(self):
    order = self.create_order_default()
    # Edit 2017-07: Fill qty does not have to match with order qty because it could be a "fill qty (shares)" vs "order amount (currency)"
    #with self.assertRaises(ValidationError):
    #  f1 = create_fill(    fill_text="test fill",     days=-1, asset=self.a1a, fill_side=BUY,  fill_qty_unsigned=20, fill_price=2,     dedicated_to_order=order)
    f1 = create_fill(    fill_text="test fill",     days=-1, asset=self.a1a, fill_side=BUY,  fill_qty_unsigned=20, fill_price=2,     dedicated_to_order=order, custodian=self.cust, user=self.user)
    self.assertTrue(True)

  def test_clean_invalid_dedicated_order_side(self):
    order = self.create_order_default()
    with self.assertRaises(ValidationError):
      f1 = create_fill(    fill_text="test fill",     days=-1, asset=self.a1a, fill_side=SELL,  fill_qty_unsigned=10, fill_price=2,     dedicated_to_order=order)

  def test_clean_invalid_dedicated_order_asset(self):
    order = self.create_order_default()
    a2a = create_asset(a2["symbol"],a2["exchange"],a2["name"],a2["currency"])
    with self.assertRaises(ValidationError):
      f1 = create_fill(    fill_text="test fill",     days=-1, asset=a2a, fill_side=BUY,  fill_qty_unsigned=10, fill_price=2,     dedicated_to_order=order)

  # 2017-07-04: relaxed this constraint now that orders and fills are one-to-one
  def test_clean_invalid_dedicated_order_pub_date(self):
    order = self.create_order_default()
    # with self.assertRaises(ValidationError):
    f1 = create_fill(    fill_text="test fill",     days=-30, asset=self.a1a, fill_side=BUY,  fill_qty_unsigned=10, fill_price=2,     dedicated_to_order=order, custodian=self.cust, user=self.user)

  def test_clean_valid_dedicated_order(self):
    order = self.create_order_default()
    f1 = self.create_fill_from_order_default(order=order, fill_price=22)

  # two opposite fills  within the same minute with the same quantities
  # cause an error: ZeroDivisionError: Weights sum to zero, can't be normalized
  # zipline_app/matcher.py", line 146, in <lambda>
  # grouped_close = grouped.apply(lambda g: numpy.average(g['close'],weights=g['volume']))
  # EDIT: matcher was removed from the repository of ffa-blotter (kept in django-zipline-2)
  #       but the test below is kept just for the sake of being nice to tests :D
  def test_two_opposite_fills_same_minute(self):
    qty = 10
    o_l = self.create_order_default(order_text="buy order",  order_side=BUY,  order_qty_unsigned=qty)
    o_s = self.create_order_default(order_text="sell order", order_side=SELL, order_qty_unsigned=qty)
    f_l = self.create_fill_from_order_default(order=o_l, fill_text="test fill buy")
    f_s = self.create_fill_from_order_default(order=o_s, fill_text="test fill sell")

  def test_dedicated_fill_with_earlier_open_fill(self):
    o1 = self.create_order_default(order_text="random order 1", days=-1, order_qty_unsigned=10)
    o2 = self.create_order_default(order_text="random order 2", days=-2, order_qty_unsigned=20)
    o3 = self.create_order_default(order_text="random order 3", days=-3, order_qty_unsigned=30)
    f1 = self.create_fill_from_order_default(order=o1, fill_price=1, fill_text="fill 1")

    self.assertEqual(o1.order_qty_signed(), o1.filled())
    self.assertEqual(o3.filled(),0)

    # deleting the fill should make the order unfilled again
    f1.delete()
    # for some reason, o1.refresh_from_db() was not sufficient
    # so get the order again with a queryset
    o4 = Order.objects.filter(order_text="random order 1")
    self.assertEqual(o4.first().filled(),0)

  def test_dedicated_fill_delete(self):
    o1 = self.create_order_default()
    f1 = self.create_fill_from_order_default(order=o1, fill_price=1, fill_text="fill 1")
    f1.delete()

  def test_fill_with_user(self):
    password='bla'
    f1 = self.create_fill_from_order_default(fill_price=1, fill_text="fill 1")

  # https://docs.djangoproject.com/en/1.10/topics/testing/tools/#email-services
  def test_create_fill_sends_email(self):
    f1 = self.create_fill_from_order_default(fill_price=1, fill_text="fill 1")
    self.assertEqual(len(mail.outbox), 1+1) # 1 email for order, and another for the fill
    self.assertTrue("New order" in mail.outbox[0].subject)
    self.assertTrue("New fill" in mail.outbox[1].subject)

    # check appended summary
    self.assertTrue("Open: 0" in mail.outbox[1].body)
    self.assertTrue("Placed: 0" in mail.outbox[1].body)
    self.assertTrue("Filled: 1" in mail.outbox[1].body)

class FillGeneralViewsTests(FillBaseTests):
    def setUp(self):
      super(FillGeneralViewsTests, self).setUp()
      self.url_new = reverse('zipline_app:fills-new', kwargs={'order': self.o1.id})

    def test_list(self):
        url = reverse('zipline_app:fills-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_new(self):
        response = self.client.get(self.url_new)
        self.assertEqual(response.status_code, 200)

    def test_delete(self):
        f1 = self.create_fill_from_order_default()
        url = reverse('zipline_app:fills-delete', args=(f1.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_quantity_large_does_not_trigger_error_integer_too_large(self):
        time = '2015-01-01 00:00:00' #timezone.now() + datetime.timedelta(days=-0.5)
        largeqty=100000000000000000000000000000
        in1 =  {
          'pub_date':time,
          'asset':self.a1a.id,
          'fill_side': BUY,
          'fill_qty_unsigned':largeqty,
          'fill_price':1,
          'category': 'P',
          'trade_date': '2000-01-01',
          'settlement_date': '2000-01-01',
          'custodian': self.cust.id,
          'dedicated_to_order': self.o1.id
        }
        response = self.client.post( self.url_new, in1)
        # 2017-08-04: fill qty is not independent of order qty, and can represent shares if order represents currency, and vice versa
        # 2017-07-04: this now is supposed to pass instead of throw error because the form qty is taken from the order
        #   make sure we get a 302 return code
        # print(list(response))
        # self.assertEqual(response.status_code, 302)
        self.assertContains(response,"Ensure this value is less than or equal to")
        in1['fill_qty_unsigned'] = 1
        in1['fill_price'] = largeqty
        response = self.client.post(url, in1, follow=True)
        self.assertContains(response,"Ensure this value is less than or equal to")

    def test_update_get(self):
        f1 = self.create_fill_from_order_default()
        url = reverse('zipline_app:fills-update', args=(f1.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_update_post_wo_tt_order_key(self):
        f1 = self.create_fill_from_order_default()
        url = reverse('zipline_app:fills-update', args=(f1.id,))
        f2={'pub_date':f1.pub_date, 'asset':f1.asset.id, 'fill_side': f1.fill_side, 'fill_qty_unsigned':4444, 'fill_price':f1.fill_price, 'source':'concealed'}
        response = self.client.post(url,f2)
        self.assertContains(response,"4444")

    def test_update_post_wi_tt_order_key(self):
        f1 = self.create_fill_from_order_default(tt_order_key='bla key')
        url = reverse('zipline_app:fills-update', args=(f1.id,))
        f1={'pub_date':f1.pub_date, 'asset':f1.asset.id, 'fill_side': f1.fill_side, 'fill_qty_unsigned':f1.fill_qty_unsigned, 'fill_price':f1.fill_price, 'tt_order_key':'foo key'}
        response = self.client.post(url,f1)
        self.assertContains(response,"foo key")

    def test_new_fill_GET(self):
        response = self.client.get(self.url_new)
        self.assertContains(response,"10")

    def test_new_fill_zero_qty(self):
        time = '2015-01-01 06:00:00'
        f1={
          'pub_date':time,
          'asset':self.a1a.id,
          'fill_side': BUY,
          'fill_qty_unsigned':0,
          'fill_price':1,
          'category': PRINCIPAL,
          'is_internal': False,
          'trade_date': '2000-01-01',
          'settlement_date': '2000-01-01',
          'custodian': self.cust.id,
          'dedicated_to_order': self.o1.id
        }
        response = self.client.post(self.url_new,f1)
        # 2017-08-04: fill qty is independent of order qty now (shares vs currency)
        # 2017-07-09: now that the fill is linked to the order, the qty submitted is cleaned to be the same from the order, so the above POST will pass successfully
        # print(list(response))
        self.assertContains(response,"Quantity 0.0 is not allowed")
        # self.assertEqual(response.status_code, 302)

    def test_new_fill_negative_price(self):
        time = '2015-01-01 06:00:00'
        f1={
          'pub_date':time,
          'asset':self.a1a.id,
          'fill_side': BUY,
          'fill_qty_unsigned':1,
          'fill_price':-1,
          'category': PRINCIPAL,
          'is_internal': False,
          'trade_date': '2000-01-01',
          'dedicated_to_order': self.o1.id
        }
        response = self.client.post(self.url_new,f1)
        self.assertContains(response,"Enter a positive number.")

    def test_new_fill_dedicated_to_order(self):
        f1={
          'pub_date':self.o1.pub_date.astimezone(get_current_timezone()).strftime('%Y-%m-%d %H:%M'),
          'asset':self.o1.asset.id,
          'fill_side': self.o1.order_side,
          'fill_qty_unsigned':self.o1.order_qty_unsigned,
          'fill_unit': SHARE,
          'fill_price':1,
          'dedicated_to_order':self.o1.id,
          'category': PRINCIPAL,
          'is_internal': False,
          'trade_date': '2000-01-01',
          'settlement_date': '2000-01-01',
          'custodian': self.cust.id,
          'dedicated_to_order': self.o1.id
        }
        response = self.client.post(self.url_new,f1,follow=True)

        expected = reverse('zipline_app:orders-detail', args=(self.o1.id,))
        # print(list(response))
        self.assertNotContains(response, "has-error")
        self.assertContains(response, expected)

        # check that username is showing up
        self.assertEqual(b''.join(list(response)).count(b"john"),2)

    def test_new_fill_user_not_dedicated(self):
      # intentionally do not pass order here
      # Edit 2017-08-15: updated url pattern to force requiring the order id
      #                  Because of this, the failure is earlier, at the 'reverse' call
      with self.assertRaises(Exception):
        url = reverse('zipline_app:fills-new') #, kwargs={'order': self.o1.id})

def url_permission(test, url, obj_id):
  url = reverse(url, args=(obj_id,))

  # note that this GET for a fills-delete or orders-delete displays a CONFIRM and hence doesnt delete the fill/order
  response = test.client.get(url, follow=False)
  test.assertEqual(response.status_code, 200)

  password='bla'
  u2 = User.objects.create_user(username='ringo', email='ringo@beatles.com', password=password)
  test.client.logout()
  response = test.client.login(username=u2.username, password=password)
  test.assertEqual(response, True)

  response = test.client.get(url, follow=False)
  test.assertEqual(response.status_code, 403) # permission denied

class FillDetailViewsTests(FillBaseTests):
  def test_detail_edit_del_only_for_owner(self):
    f1 = self.create_fill_from_order_default()

    url = reverse('zipline_app:fills-detail', args=(f1.id,))

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
    f1 = self.create_fill_from_order_default()
    url_permission(self, 'zipline_app:fills-update', f1.id)

  def test_del_only_for_owner(self):
    f1 = self.create_fill_from_order_default()
    url_permission(self, 'zipline_app:fills-delete', f1.id)
