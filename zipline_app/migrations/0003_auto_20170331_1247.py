# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-03-31 09:47
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('zipline_app', '0002_auto_20170331_0753'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='order_validity',
            field=models.CharField(choices=[('C', 'GTC order'), ('D', 'GTD order'), ('-', 'Day order')], default='C', max_length=1),
        ),
        migrations.AddField(
            model_name='order',
            name='validity_date',
            field=models.DateTimeField(blank=True, default=None, null=True),
        ),
        migrations.AddField(
            model_name='orderhistory',
            name='order_validity',
            field=models.CharField(choices=[('C', 'GTC order'), ('D', 'GTD order'), ('-', 'Day order')], default='C', max_length=1),
        ),
        migrations.AddField(
            model_name='orderhistory',
            name='validity_date',
            field=models.DateTimeField(blank=True, default=None, null=True),
        ),
    ]