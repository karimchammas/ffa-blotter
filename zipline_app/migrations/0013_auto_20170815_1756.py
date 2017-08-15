# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-08-15 14:56
from __future__ import unicode_literals

from django.db import migrations, models
import zipline_app.utils


class Migration(migrations.Migration):

    dependencies = [
        ('zipline_app', '0012_auto_20170809_1225'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='pub_date',
            field=models.DateTimeField(default=zipline_app.utils.now_minute, verbose_name='Date'),
        ),
        migrations.AlterField(
            model_name='orderhistory',
            name='pub_date',
            field=models.DateTimeField(default=zipline_app.utils.now_minute, verbose_name='Date'),
        ),
    ]
