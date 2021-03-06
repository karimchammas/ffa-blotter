# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-07-09 10:29
from __future__ import unicode_literals

import datetime
import django.core.validators
from django.db import migrations, models
import zipline_app.models.zipline_app.side


class Migration(migrations.Migration):

    replaces = [('zipline_app', '0003_asset_asset_isin'), ('zipline_app', '0004_auto_20170620_1720'), ('zipline_app', '0005_auto_20170620_1918'), ('zipline_app', '0006_auto_20170703_1146'), ('zipline_app', '0007_fill_status'), ('zipline_app', '0008_fill_category'), ('zipline_app', '0009_fill_is_internal'), ('zipline_app', '0010_fill_trade_date'), ('zipline_app', '0011_auto_20170704_1412'), ('zipline_app', '0012_remove_fill_votes')]

    dependencies = [
        ('zipline_app', '0002_auto_20170331_0753_squashed_0005_auto_20170331_1432'),
    ]

    operations = [
        migrations.AddField(
            model_name='asset',
            name='asset_isin',
            field=models.CharField(max_length=20, null=True),
        ),
        migrations.AddField(
            model_name='order',
            name='am_type',
            field=models.CharField(choices=[('N', 'None'), ('U', 'Unsolicited'), ('D', 'Discretionary')], default='N', max_length=1, verbose_name='AM Type'),
        ),
        migrations.AddField(
            model_name='orderhistory',
            name='am_type',
            field=models.CharField(choices=[('N', 'None'), ('U', 'Unsolicited'), ('D', 'Discretionary')], default='N', max_length=1, verbose_name='AM Type'),
        ),
        migrations.AlterField(
            model_name='order',
            name='order_type',
            field=models.CharField(choices=[('M', 'Market'), ('L', 'Limit')], default='M', max_length=1, verbose_name='Execution'),
        ),
        migrations.AlterField(
            model_name='orderhistory',
            name='order_type',
            field=models.CharField(choices=[('M', 'Market'), ('L', 'Limit')], default='M', max_length=1, verbose_name='Execution'),
        ),
        migrations.AddField(
            model_name='asset',
            name='asset_currency',
            field=models.CharField(max_length=20, null=True),
        ),
        migrations.AddField(
            model_name='order',
            name='order_qty_unit',
            field=models.CharField(default='shares', max_length=20, verbose_name='Qty unit'),
        ),
        migrations.AddField(
            model_name='orderhistory',
            name='order_qty_unit',
            field=models.CharField(default='shares', max_length=20, verbose_name='Qty unit'),
        ),
        migrations.AddField(
            model_name='order',
            name='commission',
            field=zipline_app.models.zipline_app.side.PositiveFloatFieldModel(blank=True, default=0, null=True, validators=[django.core.validators.MaxValueValidator(1000000), django.core.validators.MinValueValidator(0)]),
        ),
        migrations.AddField(
            model_name='orderhistory',
            name='commission',
            field=zipline_app.models.zipline_app.side.PositiveFloatFieldModel(blank=True, default=0, null=True, validators=[django.core.validators.MaxValueValidator(1000000), django.core.validators.MinValueValidator(0)]),
        ),
        migrations.AddField(
            model_name='fill',
            name='fill_status',
            field=models.CharField(choices=[('P', 'Placed'), ('C', 'Completed')], default='P', max_length=1, verbose_name='Status'),
        ),
        migrations.AddField(
            model_name='fill',
            name='category',
            field=models.CharField(choices=[('P', 'Principal'), ('A', 'Agent')], default='P', max_length=1, verbose_name='Order Category'),
        ),
        migrations.AddField(
            model_name='fill',
            name='is_internal',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='fill',
            name='trade_date',
            field=models.DateField(default=datetime.date.today, verbose_name='trade date'),
        ),
        migrations.RemoveField(
            model_name='fill',
            name='votes',
        ),
    ]
