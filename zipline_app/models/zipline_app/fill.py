from __future__ import unicode_literals

from django.db import models
from django.utils import timezone
import datetime
from django.urls import reverse

from .asset import Asset
from .order import Order, ORDER_UNIT_CHOICES, SHARE
from .custodian import Custodian
from .side import BUY, FILL_SIDE_CHOICES, validate_nonzero, PositiveFloatFieldForm, PositiveFloatFieldModel, PRINCIPAL, FILL_CATEGORY_CHOICES
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from ...utils import now_minute, chopSeconds
from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator

class Fill(models.Model):
    # 2017-03-17: relink fill to order as a "dedicated to order" field
    # 2017-01-12: unlink orders from fills and use zipline engine to perform matching
    # order = models.ForeignKey(Order, on_delete=models.CASCADE)
    dedicated_to_order = models.OneToOneField(Order, null=True, blank=False, verbose_name="Order", on_delete=models.SET_NULL)

    fill_text = models.CharField(max_length=200, blank=True)
    # 2017-08-04: https://github.com/shadiakiki1986/ffa-blotter/issues/73
    #             Allow decimals (for shares)
    # fill_qty_unsigned = models.PositiveIntegerField(
    fill_qty_unsigned = PositiveFloatFieldModel(
      default=0,
      validators=[validate_nonzero],
      verbose_name="Qty/Amount"
    )
    fill_price = PositiveFloatFieldModel(
      default=0,
      validators=[validate_nonzero],
    )
    pub_date = models.DateTimeField('date published',default=now_minute)
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, null=True)
    tt_order_key = models.CharField(max_length=20, blank=True)

    fill_side = models.CharField(
      max_length=1,
      choices=FILL_SIDE_CHOICES,
      default=BUY,
      verbose_name="Side"
    )
    user = models.ForeignKey(User, null=True, default=None)
    category = models.CharField(
      max_length=1,
      choices=FILL_CATEGORY_CHOICES,
      default=PRINCIPAL,
      verbose_name="Order Category"
    )
    is_internal = models.BooleanField(default=False)
    trade_date = models.DateField('trade date',default=datetime.date.today)
    settlement_date = models.DateField('settlement date',default=datetime.date.today)
    custodian = models.ForeignKey(Custodian, on_delete=models.CASCADE, null=True)
    fill_unit = models.CharField(
      max_length=1,
      choices=ORDER_UNIT_CHOICES,
      default=SHARE,
      verbose_name="Unit"
    )

    commission = PositiveFloatFieldModel(
      default=0,
      validators=[MaxValueValidator(100), MinValueValidator(0)],
      null=True,
      blank=True
    )

    def get_is_internal_display(self):
      if self.is_internal: return "Internal"
      return "External"

    def fill_qty_signed(self):
      return self.fill_qty_unsigned * (+1 if self.fill_side==BUY else -1)

    def __str__(self):
        return "%s, %s %s, %s (%s, %s)%s" % (
          self.asset.asset_symbol, self.fill_side, self.fill_qty_unsigned, self.fill_price, self.tt_order_key, self.fill_text,
          "" if self.dedicated_to_order is None else " - dedicated to %s"%self.dedicated_to_order
        )

    # validating a model
    # https://docs.djangoproject.com/en/1.10/ref/models/instances/#django.db.models.Model.clean
    def clean(self):
      # drop seconds from pub_date
      self.pub_date = chopSeconds(self.pub_date)

      # check that linked order matches with local properties
      if self.dedicated_to_order is not None:
        errors = {}
        if self.fill_side!=self.dedicated_to_order.order_side:
          errors['fill_side']=_('Dedicated fill side doesnt match with order')
        if self.asset!=self.dedicated_to_order.asset:
          errors['asset']=_('Dedicated fill asset doesnt match with order')

        # 2017-07-04: since all fills are dedicated to orders, relax this constraint, to gain the real creation date of the fill
        #if self.pub_date!=self.dedicated_to_order.pub_date:
        #  errors['pub_date']=_(
        #    'Dedicated fill date (%s) doesnt match with order (%s)'
        #    %(
        #      self.pub_date,
        #      self.dedicated_to_order.pub_date
        #    )
        #  )

        if len(errors)>0:
          raise ValidationError(errors)

# using get_success_url
#    def get_absolute_url(self):
#      return reverse('zipline_app:fills-list') # TODO rename to fills
#      return reverse('zipline_app:fills-list', kwargs={'pk': self.pk})

    # copy from order
    def my_get_fill_unit_display(self):
      if self.fill_unit==SHARE: return "share"
      return self.asset.asset_currency
