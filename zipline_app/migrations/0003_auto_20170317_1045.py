# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-03-17 08:45
from __future__ import unicode_literals

import django.core.validators
from django.db import migrations, models
import zipline_app.models.zipline_app.fill


class Migration(migrations.Migration):

    dependencies = [
        ('zipline_app', '0002_auto_20170316_1235'),
    ]

    operations = [
        migrations.AlterField(
            model_name='fill',
            name='fill_qty_unsigned',
            field=models.PositiveIntegerField(default=0, validators=[django.core.validators.MaxValueValidator(1000000), zipline_app.models.zipline_app.fill.validate_nonzero], verbose_name='Qty'),
        ),
        migrations.AlterField(
            model_name='fill',
            name='fill_side',
            field=models.CharField(choices=[('L', 'Long'), ('S', 'Short')], default='L', max_length=1, verbose_name='Side'),
        ),
        migrations.AlterField(
            model_name='order',
            name='amount_unsigned',
            field=models.PositiveIntegerField(default=0, validators=[django.core.validators.MaxValueValidator(1000000), zipline_app.models.zipline_app.fill.validate_nonzero], verbose_name='Qty'),
        ),
        migrations.AlterField(
            model_name='order',
            name='order_side',
            field=models.CharField(choices=[('L', 'Long'), ('S', 'Short')], default='L', max_length=1, verbose_name='Side'),
        ),
    ]
