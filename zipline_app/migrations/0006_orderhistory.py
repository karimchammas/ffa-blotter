# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-03-27 13:24
from __future__ import unicode_literals

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import zipline_app.models.zipline_app.side
import zipline_app.utils


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('zipline_app', '0005_auto_20170327_1515'),
    ]

    operations = [
        migrations.CreateModel(
            name='OrderHistory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order_text', models.CharField(blank=True, max_length=200)),
                ('pub_date', models.DateTimeField(default=zipline_app.utils.now_minute, verbose_name='date published')),
                ('amount_unsigned', models.PositiveIntegerField(default=0, validators=[django.core.validators.MaxValueValidator(1000000), zipline_app.models.zipline_app.side.validate_nonzero], verbose_name='Qty')),
                ('order_side', models.CharField(choices=[('L', 'Long'), ('S', 'Short')], default='L', max_length=1, verbose_name='Side')),
                ('order_type', models.CharField(choices=[('M', 'Market'), ('L', 'Limit')], default='M', max_length=1, verbose_name='Type')),
                ('limit_price', zipline_app.models.zipline_app.side.PositiveFloatFieldModel(default=0, validators=[django.core.validators.MaxValueValidator(1000000), django.core.validators.MinValueValidator(0), zipline_app.models.zipline_app.side.validate_nonzero])),
                ('account', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='zipline_app.Account')),
                ('asset', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='zipline_app.Asset')),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='zipline_app.Order')),
                ('previous', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='zipline_app.OrderHistory')),
                ('user', models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
