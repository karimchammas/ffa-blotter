from __future__ import unicode_literals

from django.db import models
class Account(models.Model):
    account_symbol = models.CharField(max_length=20,  unique=True)
    account_name   = models.CharField(max_length=200, default="")
    account_origin = models.CharField(max_length=20,  default="Manual")

    def __str__(self):
      return "%s: %s (%s)" % (self.account_symbol, self.account_name, self.account_origin)

    def get_absolute_url(self):
      return reverse('zipline_app:accounts-list') # TODO rename to accounts
#      return reverse('zipline_app:accounts-list', kwargs={'pk': self.pk})

    def delete(self):
      if self.order_set.count()>0:
        raise ValueError("Cannot delete account because it is linked to orders")
