from django.test import TestCase

# Testing management commands
# https://docs.djangoproject.com/en/1.10/topics/testing/tools/#management-commands
from django.core.management import call_command
from django.utils.six import StringIO

from ...models.zipline_app.side import BUY
from .test_zipline_app import OrderBaseTests
from django.core import mail
from ...utils import myTestLogin

class ReminderCommandTests(OrderBaseTests):
  def testMain(self):
    with StringIO() as out, StringIO() as err:
      o1 = self.create_order_default()
      call_command('reminder', stderr=err, stdout=out, debug=True)
      # print([x.subject for x in mail.outbox])
      self.assertEqual(len(mail.outbox), 2) # 1 email for creating the order, and another for the reminder

  def testNoRecipients(self):
    with StringIO() as out, StringIO() as err:
      self.user.email = ''
      self.user.save()
      o1 = self.create_order_default()
      call_command('reminder', stderr=err, stdout=out, debug=True)
      # print([x.subject for x in mail.outbox])
      self.assertEqual(len(mail.outbox), 0) # only 1 email about created order
      self.assertNotIn("Failed", err.getvalue())
      self.assertIn("No users", err.getvalue())
      self.assertEquals(out.getvalue(), "")

  def testNoOrders(self):
    with StringIO() as out, StringIO() as err:
      call_command('reminder', stderr=err, stdout=out, debug=True)
      self.assertEqual(len(mail.outbox), 0)
      self.assertNotIn("Failed", err.getvalue())
      self.assertIn("No pending", err.getvalue())
      self.assertEquals(out.getvalue(), "")
