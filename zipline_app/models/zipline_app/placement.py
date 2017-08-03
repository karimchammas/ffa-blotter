from __future__ import unicode_literals
from django.db import models
from .order import Order
from ...utils import now_minute
from django.contrib.auth.models import User

class Placement(models.Model):
  order = models.OneToOneField(Order, on_delete=models.CASCADE, verbose_name="Order")
  date = models.DateTimeField(verbose_name = 'Placement date',default=now_minute)
  user = models.ForeignKey(User)

  def __str__(self):
    return "Order #%s, Date: %s, User: %s" % (
      self.order.id, self.date, self.user.username
    )
