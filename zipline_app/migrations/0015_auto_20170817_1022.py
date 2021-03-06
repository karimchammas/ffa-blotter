# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-08-17 07:22
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('zipline_app', '0014_auto_20170817_1020'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='asset',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='zipline_app.Asset', verbose_name='Security'),
        ),
        migrations.AlterField(
            model_name='orderhistory',
            name='asset',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='zipline_app.Asset', verbose_name='Security'),
        ),
    ]
