from __future__ import unicode_literals

# Django Logging
# https://docs.djangoproject.com/en/1.10/topics/logging/
import logging
logger = logging.getLogger("zipline_app") #__name__)

from .models.zipline_app.fill import Fill
from .utils import email_ctx
from .views.zipline_app.order import get_stats_orders

# https://docs.djangoproject.com/en/1.11/topics/signals/#connecting-receiver-functions

class SignalProcessor:
  #def post_init(sender, **kwargs):
  #  print("Signal: %s, %s" % ("post_init", sender.__name__))

  def post_save(sender, instance, created, **kwargs):
    logger.debug("Signal: %s, %s" % ("post_save", sender.__name__))

    context = {'stats_orders': get_stats_orders()}
    if sender.__name__=="Fill":
      if created:
        subject = None
        if instance.dedicated_to_order is not None:
          order = instance.dedicated_to_order
          subject = "New fill #%s (fills order #%s)" % (instance.id, order.id)
        else:
          subject = "New fill #%s (%s x %s)" % (instance.id, instance.fill_qty_signed(), instance.asset.asset_name)

        context['fill'] = instance
        email_ctx(
          context,
          'zipline_app/email_fill_plain.txt',
          'zipline_app/fill/_fill_detail.html',
          subject,
          logger
        )

    if sender.__name__=="Order":
      logger.debug("post_save order %s"%created)
      if created:
        subject = "New order #%s (%s x %s)" % (instance.id, instance.order_qty_signed(), instance.asset.asset_name)
        context['order'] = instance
        email_ctx(
          context,
          'zipline_app/email_order_plain.txt',
          'zipline_app/order/_order_detail.html',
          subject,
          logger
        )

    if sender.__name__=="Placement":
      logger.debug("post_save placement %s"%created)
      if created:
        subject = "Placement for order #%s" % (instance.order.id)
        context['placement'] = instance
        email_ctx(
          context,
          'zipline_app/email_placement.txt',
          'zipline_app/email_placement.html',
          subject,
          logger
        )
