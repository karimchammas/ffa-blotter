from django.test import TestCase
from ...utils import chopSeconds, now_minute, get_revision_diffs
from django.utils import timezone
import reversion
from .test_zipline_app import OrderBaseTests, create_account, create_asset

class UtilsTests(OrderBaseTests):
  def test_chopSeconds(self):
    ts1 = timezone.now()
    ts2 = chopSeconds(ts1)
    self.assertEqual(ts2.second,0)
    self.assertEqual(ts2.microsecond,0)

  def test_now_minute(self):
    ts1 = timezone.now()
    ts2=now_minute()
    self.assertEqual(ts2.second,0)
    self.assertEqual(ts2.microsecond,0)
    self.assertEqual(ts2.minute,ts1.minute)
    self.assertEqual(ts2.hour,ts1.hour)

  def test_get_revision_diffs(self):
    # https://django-reversion.readthedocs.io/en/stable/api.html#creating-revisions
    # https://stackoverflow.com/a/26006433/4126114
    o1 = self.create_order_default()
    with reversion.create_revision():
      o1.save()

    revisions = get_revision_diffs(o1)
    self.assertEqual(0, len(revisions))

    with reversion.create_revision():
      o1.order_side = 'S'
      o1.save()

    revisions = get_revision_diffs(o1)
    self.assertEqual(1, len(revisions))

    version = revisions[0]
    self.assertIn('date_created', version)
    self.assertIn('diff', version)
    self.assertEqual("Changed order_side from 'B' to 'S'", version['diff'])

    acc2 = create_account(symbol="TEST02")
    with reversion.create_revision():
      o1.account = acc2
      o1.save()

    revisions = get_revision_diffs(o1)
    self.assertEqual(2, len(revisions))

    version = revisions[0]
    self.assertEqual("Changed account from 'TEST01:  (Manual)' to 'TEST02:  (Manual)'", version['diff'])
