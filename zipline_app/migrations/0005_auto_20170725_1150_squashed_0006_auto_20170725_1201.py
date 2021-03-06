# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-07-25 09:03
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    replaces = [('zipline_app', '0005_auto_20170725_1150'), ('zipline_app', '0006_auto_20170725_1201')]

    dependencies = [
        ('zipline_app', '0004_auto_20170710_0641_squashed_0005_auto_20170710_0723'),
    ]

    operations = [
        migrations.AlterField(
            model_name='asset',
            name='asset_symbol',
            field=models.CharField(max_length=20),
        ),
        migrations.AlterUniqueTogether(
            name='asset',
            unique_together=set([('asset_symbol', 'asset_origin')]),
        ),
        migrations.AlterModelOptions(
            name='asset',
            options={'ordering': ['asset_symbol', 'asset_origin']},
        ),
    ]
