# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-08-18 05:49
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('zipline_app', '0017_fill_commission'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='orderhistory',
            name='account',
        ),
        migrations.RemoveField(
            model_name='orderhistory',
            name='asset',
        ),
        migrations.RemoveField(
            model_name='orderhistory',
            name='order',
        ),
        migrations.RemoveField(
            model_name='orderhistory',
            name='previous',
        ),
        migrations.RemoveField(
            model_name='orderhistory',
            name='user',
        ),
        migrations.DeleteModel(
            name='OrderHistory',
        ),
    ]
