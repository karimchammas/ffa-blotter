from __future__ import unicode_literals

from django.db import models

from django.urls import reverse

class Asset(models.Model):
    asset_symbol = models.CharField(max_length=20)
    asset_exchange = models.CharField(max_length=200)
    asset_name = models.CharField(max_length=200)
    asset_isin = models.CharField(max_length=20, null=True)
    asset_currency = models.CharField(max_length=20, null=True)
    asset_origin = models.CharField(max_length=20,  default="Manual")

    # How to define two fields “unique” as couple
    # https://stackoverflow.com/a/2201687/4126114
    class Meta:
      unique_together = ('asset_symbol', 'asset_origin')
      ordering = ['asset_symbol', 'asset_origin']

    def __str__(self):
        return "%s: %s (%s, %s)" % (self.asset_symbol, self.asset_name, self.asset_currency, self.asset_origin)

    def str(self):
      return self.__str__()

    def to_dict(self):
        return {
          "symbol": self.asset_symbol,
          "exchange": self.asset_exchange,
          "name": self.asset_name,
          "isin": self.asset_isin,
          "currency": self.asset_currency,
          "origin": self.asset_origin
        }

    def delete(self):
      if self.order_set.count()>0:
        raise ValueError("Cannot delete asset because it is linked to orders")
      if self.fill_set.count()>0:
        raise ValueError("Cannot delete asset because it is linked to fills")

# use get_success_url instead
#    def get_absolute_url(self):
#      return reverse('zipline_app:assets-list') # TODO rename to assets
#      return reverse('zipline_app:assets-list', kwargs={'pk': self.pk})
