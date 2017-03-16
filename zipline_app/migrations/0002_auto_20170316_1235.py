# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-03-16 10:35
from __future__ import unicode_literals

import django.core.validators
from django.db import migrations, models
import zipline_app.models.zipline_app.fill


class Migration(migrations.Migration):

    dependencies = [
        ('zipline_app', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='fill',
            name='fill_qty',
        ),
        migrations.RemoveField(
            model_name='order',
            name='amount',
        ),
        migrations.AddField(
            model_name='fill',
            name='fill_qty_unsigned',
            field=models.PositiveIntegerField(default=0, validators=[django.core.validators.MaxValueValidator(1000000), zipline_app.models.zipline_app.fill.validate_nonzero]),
        ),
        migrations.AddField(
            model_name='fill',
            name='fill_side',
            field=models.CharField(choices=[('L', 'Long'), ('S', 'Short')], default='L', max_length=1),
        ),
        migrations.AddField(
            model_name='fill',
            name='tt_order_key',
            field=models.CharField(blank=True, max_length=20),
        ),
        migrations.AddField(
            model_name='order',
            name='amount_unsigned',
            field=models.PositiveIntegerField(default=0, validators=[django.core.validators.MaxValueValidator(1000000), zipline_app.models.zipline_app.fill.validate_nonzero]),
        ),
        migrations.AddField(
            model_name='order',
            name='order_side',
            field=models.CharField(choices=[('L', 'Long'), ('S', 'Short')], default='L', max_length=1),
        ),
    ]
