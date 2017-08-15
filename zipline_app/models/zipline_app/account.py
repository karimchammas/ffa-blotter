from __future__ import unicode_literals
from django.urls import  reverse_lazy

from django.db import models
class Account(models.Model):
    account_symbol = models.CharField(max_length=20,  unique=True)
    account_name   = models.CharField(max_length=200, default="")
    account_origin = models.CharField(max_length=20,  default="Manual")

    def __str__(self):
      return "%s: %s (%s)" % (self.account_symbol, self.account_name, self.account_origin)
      #return self.account_symbol

    def get_absolute_url(self):
      return reverse_lazy('zipline_app:accounts-detail', kwargs={'pk': self.pk})

    def delete(self):
      if self.order_set.count()>0:
        raise ValueError("Cannot delete account because it is linked to orders")

#    def get_account_name_display(self):
#      max_len = 10
#      need_elipsis = len(self.account_name) > max_len
#      return self.account_name[:max_len] + ('...' if need_elipsis else '')
#
#    def get_account_origin_display(self):
#      map_origin = {'MF Lebanon': 'LEB', 'MF Dubai': 'DXB'}
#      return map_origin[self.account_origin]
