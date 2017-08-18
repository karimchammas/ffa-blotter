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
  ORDER_STATUS_CHOICES, OPEN, CANCELLED, FILLED, PLACED, \
  ORDER_VALIDITY_CHOICES, GTC, GTD, DAY

from numpy import average
from django.core.validators import MaxValueValidator, MinValueValidator
from ...utils import now_minute, chopSeconds, get_revision_diffs

from django.contrib.auth.models import User

from django.utils.encoding import force_text
import reversion

# types that are specific to FFA AM
NONE = 'N'
UNSOLICITED = 'U'
DISCRETIONARY = 'D'
AM_TYPE_CHOICES = (
  (NONE, 'None'),
  (UNSOLICITED, 'Unsolicited'),
  (DISCRETIONARY, 'Discretionary'),
)
# types of units
SHARE = 'S'
CURRENCY = 'C'
ORDER_UNIT_CHOICES = (
  (SHARE, 'Share'),
  (CURRENCY, 'Currency')
)
#-----------
class AbstractOrder(models.Model):
    order_text = models.CharField(max_length=200, blank=True)
    pub_date = models.DateTimeField('Date',default=now_minute)
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, null=True, verbose_name="Security")
    # 2017-08-04: https://github.com/shadiakiki1986/ffa-blotter/issues/73
    #             Allow decimals (for shares)
    # order_qty_unsigned = models.PositiveIntegerField(
    # 2017-08-09 drop max value validator
    #  validators=[MaxValueValidator(CIRCUIT_BREAKER), validate_nonzero],
    order_qty_unsigned = PositiveFloatFieldModel(
      default=0,
      validators=[validate_nonzero],
      verbose_name="Qty/Amount"
    )
    order_unit = models.CharField(
      max_length=1,
      choices=ORDER_UNIT_CHOICES,
      default=SHARE,
      verbose_name="Unit"
    )
    account = models.ForeignKey(Account, on_delete=models.CASCADE, verbose_name="Client")
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
      validators=[validate_nonzero],
      null=True,
      blank=True
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
      validators=[MaxValueValidator(100), MinValueValidator(0)],
      null=True,
      blank=True
    )

    @property
    def order_status(self):
      if hasattr(self,'fill'): return FILLED
      if hasattr(self,'placement'): return PLACED
      if self.order_validity == GTD:
        if now_minute() > self.validity_date:
          return CANCELLED
      if self.order_validity == DAY:
        if now_minute().strftime("%Y-%m-%d") > self.pub_date.strftime("%Y-%m-%d"):
          return CANCELLED
      return OPEN

    # Copied from /home/shadi/.local/share/virtualenvs/FFA_BLOTTER/lib/python3.5/site-packages/django/db/models/base.py
    def get_order_status_display(self, value=None):
      if value is None: value = self.order_status # getattr(self, field.attname)
      field_flatchoices = ORDER_STATUS_CHOICES
      return force_text(dict(field_flatchoices).get(value, value), strings_only=True)

    def diff(self, other):
      if other is None:
        return []
      messages = []
      attrs = [
        'order_text', 'pub_date', 'asset',
        'order_qty_unsigned', 'order_unit',
        'account', 'order_side', 'order_type',
        'limit_price',
        'order_validity', 'validity_date', 'am_type',
        'commission'
      ]
      for attr in attrs:
        if not hasattr(self, attr): continue
        if not hasattr(other, attr): continue
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

#---------------------------
# http://stackoverflow.com/a/14282776/4126114
@reversion.register()
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

    # excluding the first entry with previous=None since this is available regardless of edits made
    def history(self):
      return get_revision_diffs(self)

    def my_get_order_unit_display(self):
      if self.order_unit==SHARE: return "share"
      return self.asset.asset_currency
