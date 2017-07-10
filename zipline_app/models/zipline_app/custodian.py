from __future__ import unicode_literals

from django.db import models
class Custodian(models.Model):
    custodian_symbol = models.CharField(max_length=20,  unique=True)
    custodian_name   = models.CharField(max_length=200, default="")
    custodian_origin = models.CharField(max_length=20,  default="Manual")

    def __str__(self):
      return "%s: %s (%s)" % (self.custodian_symbol, self.custodian_name, self.custodian_origin)

    def get_absolute_url(self):
      return reverse('zipline_app:custodians-list')

    def delete(self):
      if self.fill_set.count()>0:
        raise ValueError("Cannot delete custodian because it is linked to fills")
