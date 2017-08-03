from __future__ import unicode_literals

from django.apps import AppConfig
from django.db import models
# connecting signals
#from django.db.backends.signals import connection_created
from django.core.signals import request_started

class ZiplineAppConfig(AppConfig):
    name = 'zipline_app'

    # https://chriskief.com/2014/02/28/django-1-7-signals-appconfig/
    def ready(self):
      from .signalProcessor import SignalProcessor
      request_started.connect(SignalProcessor.request_started)
      # below models should be defined in models/zipline_app/zipline_app.py
      senders=("zipline_app.Order", "zipline_app.Fill", "zipline_app.Asset", "zipline_app.Placement")
      for sender in senders:
        #models.signals.post_init.connect(SignalProcessor.post_init, sender=sender)
        models.signals.post_save.connect(SignalProcessor.post_save, sender=sender)
        models.signals.post_delete.connect(SignalProcessor.post_delete, sender=sender)
