import logging
from ._mfManager import MfManager
from ...models.zipline_app.order import Order
from ...utils import email_ctx

# https://docs.djangoproject.com/en/1.10/howto/custom-management-commands/
from django.core.management.base import BaseCommand

logger = logging.getLogger('FFA blotter')

class Command(BaseCommand):
  help = """Usage:
         python manage.py reminder --help
         python manage.py reminder --debug
         """

  def add_arguments(self, parser):
    parser.add_argument('--debug', action='store_true', dest='debug', default=False, help='show higher verbosity')

  def handle(self, *args, **options):
    h1 = logging.StreamHandler(stream=self.stderr)
    logger.addHandler(h1)
    if options['debug']:
      logger.setLevel(logging.DEBUG)

    pending_placement = [o for o in Order.objects.all() if o.dedicated_fill() is None and not hasattr(o, 'placement')]
    pending_confirmation = [o for o in Order.objects.filter(is_confirmed=False)]

    if len(pending_placement)==0 and len(pending_confirmation)==0:
      logger.debug("No pending orders")
      self.closeLogger(h1, logger)
      return

    logger.debug("Emailing about pending orders")
    email_ctx(
      {
        'pending_placement': pending_placement,
        'num_pending_placement': len(pending_placement),
        'pending_confirmation': pending_confirmation,
        'num_pending_confirmation': len(pending_confirmation),
      },
      'zipline_app/reminder.txt',
      'zipline_app/reminder.html',
      "Reminder of pending orders",
      logger
    )
    self.closeLogger(h1, logger)

  # http://bugs.python.org/issue6333#msg90328
  def closeLogger(self, h1, logger):
    logger.removeHandler(h1)
    h1.close()
