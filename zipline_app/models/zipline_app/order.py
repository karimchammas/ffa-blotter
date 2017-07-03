from __future__ import unicode_literals

from django.db import models
from django.utils import timezone
import datetime
from django.urls import reverse

from .asset import Asset
from .account import Account
from .side import BUY, FILL_SIDE_CHOICES, \
  validate_nonzero, \
  MARKET, ORDER_TYPE_CHOICES, \
  PositiveFloatFieldModel, \
  ORDER_STATUS_CHOICES, OPEN, CANCELLED, FILLED, \
  ORDER_VALIDITY_CHOICES, GTC, GTD, DAY

from numpy import average
from django.core.validators import MaxValueValidator, MinValueValidator
from ...utils import now_minute, chopSeconds
from django.contrib.auth.models import User

# types that are specific to FFA AM
NONE = 'N'
UNSOLICITED = 'U'
DISCRETIONARY = 'D'
AM_TYPE_CHOICES = (
  (NONE, 'None'),
  (UNSOLICITED, 'Unsolicited'),
  (DISCRETIONARY, 'Discretionary'),
)
class AbstractOrder(models.Model):
    order_text = models.CharField(max_length=200, blank=True)
    pub_date = models.DateTimeField('date published',default=now_minute)
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, null=True)
    order_qty_unsigned = models.PositiveIntegerField(
      default=0,
      validators=[MaxValueValidator(1000000), validate_nonzero],
      verbose_name="Qty"
    )
    order_qty_unit = models.CharField(
      max_length=20,
      default="shares",
      verbose_name="Qty unit"
    )
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    order_side = models.CharField(
      max_length=1,
      choices=FILL_SIDE_CHOICES,
      default=BUY,
      verbose_name="Side"
    )
    user = models.ForeignKey(User, null=True, default=None)
    order_type = models.CharField(
      max_length=1,
      choices=ORDER_TYPE_CHOICES,
      default=MARKET,
      verbose_name="Execution"
    )
    limit_price = PositiveFloatFieldModel(
      default=None,
      validators=[MaxValueValidator(1000000), MinValueValidator(0), validate_nonzero],
      null=True,
      blank=True
    )
    order_status = models.CharField(
      max_length=1,
      choices=ORDER_STATUS_CHOICES,
      default=OPEN,
      verbose_name="Status"
    )
    order_validity = models.CharField(
      max_length=1,
      choices=ORDER_VALIDITY_CHOICES,
      default=GTC,
      verbose_name="Validity"
    )
    validity_date = models.DateTimeField(
      default=None,
      null=True,
      blank=True,
      help_text='YYYY-MM-DD'
    )
    am_type = models.CharField(
      max_length=1,
      choices=AM_TYPE_CHOICES,
      default=NONE,
      verbose_name="AM Type"
    )
    commission = PositiveFloatFieldModel(
      default=0,
      validators=[MaxValueValidator(1000000), MinValueValidator(0)],
      null=True,
      blank=True
    )

    def diff(self, other):
      if other is None:
        return []
      messages = []
      attrs = [
        'order_text', 'pub_date', 'asset',
        'order_qty_unsigned', 'order_qty_unit',
        'account', 'order_side', 'order_type',
        'limit_price', 'order_status',
        'order_validity', 'validity_date', 'am_type',
        'commission'
      ]
      for attr in attrs:
        if getattr(self, attr) != getattr(other, attr):
          messages.append(
            "Changed %s from '%s' to '%s'" %
            (
              attr,
              getattr(other, attr),
              getattr(self, attr)
            )
          )
      return messages

    class Meta:
      abstract=True


class Order(AbstractOrder):
    def order_qty_signed(self):
      return self.order_qty_unsigned * (+1 if self.order_side==BUY else -1)

    def __str__(self):
        return "%s, %s, %s (%s, %s)" % (self.asset.asset_symbol, self.order_side, self.order_qty_unsigned, self.account.account_symbol, self.order_text)

    def was_published_recently(self):
        now = timezone.now()
        return now >= self.pub_date >= now - datetime.timedelta(days=1)

    def filled(self):
      fill = self.dedicated_fill()
      if fill is None: return 0
      return fill.fill_qty_signed()

    def fills(self):
      if self.filled()==0: return []

      fill = self.dedicated_fill()
      txn = {
        'order_id':self.id,
        'price': fill.fill_price,
        'amount': fill.fill_qty_signed(),
        'dt': fill.pub_date,
        'sid': {
          'symbol': fill.asset.asset_symbol,
        },
      }
      return [txn]

    def avgPrice(self):
      if self.filled()==0:
        return float('nan')

      sub = self.fills()
      avg = average(a=[txn["price"] for txn in sub], weights=[txn["amount"] for txn in sub])
      return avg

    def clean(self):
      # drop seconds from pub_date
      self.pub_date = chopSeconds(self.pub_date)
      # validity_date: replace hours/mins/seconds with 23:59:59
      if self.validity_date is not None:
        self.validity_date = self.validity_date.replace(hour=23, minute=59, second=59)

    # access one-to-one reverse field
    # https://docs.djangoproject.com/en/1.10/topics/db/examples/one_to_one/
    def dedicated_fill(self):
      if hasattr(self,'fill'):
        return self.fill
      return None

    was_published_recently.admin_order_field = 'pub_date'
    was_published_recently.boolean = True
    was_published_recently.short_description = 'Published recently?'

    def append_history(self):
      history = OrderHistory.objects.filter(order=self)
      previous = None
      if history.count()>0:
        previous = history.latest('id')
        diff = self.diff(previous)
        if len(diff)==0:
          return

      OrderHistory.objects.create(
        order=self,
        previous = previous,
        order_text = self.order_text,
        pub_date = self.pub_date,
        asset = self.asset,
        order_qty_unsigned = self.order_qty_unsigned,
        order_qty_unit = self.order_qty_unit,
        account = self.account,
        order_side = self.order_side,
        user = self.user,
        order_type = self.order_type,
        limit_price = self.limit_price,
        order_status = self.order_status,
        order_validity = self.order_validity,
        validity_date = self.validity_date,
        am_type = self.am_type,
        commission = self.commission
      )

    # excluding the first entry with previous=None since this is available regardless of edits made
    def history(self):
      return self.orderhistory_set.exclude(previous=None).order_by('-ed_date')

    def cancel(self):
      self.order_status = CANCELLED
      self.save()

    def setFilled(self):
      self.order_status = FILLED
      self.save()

    def setOpen(self):
      self.order_status = OPEN
      self.save()

#####################
# Model History in Django
# http://stackoverflow.com/a/14282776/4126114
class OrderHistory(AbstractOrder):
  order = models.ForeignKey(Order)
  previous = models.ForeignKey('self', null=True)
  ed_date = models.DateTimeField('date edited',default=timezone.now)

  def __str__(self):
    return ', '.join(self.diffPrevious())

  def diffPrevious(self):
    return self.diff(self.previous)

################
# Class that cancels day orders opened in the past 
#
# https://stackoverflow.com/a/37635851/4126114
# from django.db.models import F
class OrderManager:
  def process(self):
    # set status for filled orders
    #qs = Order.objects.filter(order_status=OPEN)
    #for order in qs:
    #  if order.filled() == order.order_qty_signed():
    #    raise Exception("Found filled order with status=OPEN")
    #    # order.setFilled()

    # cancel DAY orders from the past
    midnight = timezone.now().replace(hour=0, minute=0, second=0)
    qs = Order.objects.filter(order_validity=DAY, pub_date__lt=midnight, order_status=OPEN)
    for order in qs:
      order.cancel()

    # cancel GTD orders not filled yet and which expired
    now = timezone.now()
    qs = Order.objects.filter(order_validity=GTD, validity_date__lt=now, order_status=OPEN)
    for order in qs:
      order.cancel()
