# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-07-10 03:41
from __future__ import unicode_literals

import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('zipline_app', '0003_asset_asset_isin_squashed_0012_remove_fill_votes'),
    ]

    operations = [
        migrations.CreateModel(
            name='Custodian',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('custodian_symbol', models.CharField(max_length=20, unique=True)),
                ('custodian_name', models.CharField(default='', max_length=200)),
            ],
        ),
        migrations.AddField(
            model_name='fill',
            name='settlement_date',
            field=models.DateField(default=datetime.date.today, verbose_name='settlement date'),
        ),
        migrations.AddField(
            model_name='fill',
            name='custodian',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='zipline_app.Custodian'),
        ),
    ]
