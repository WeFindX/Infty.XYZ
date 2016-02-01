# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='CoinAddress',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('currency_code', models.CharField(max_length=6)),
                ('address', models.CharField(max_length=255)),
                ('user', models.ForeignKey(related_name='address', blank=True, to=settings.AUTH_USER_MODEL, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='CryptsyCredential',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('privatekey', models.CharField(unique=True, max_length=255)),
                ('publickey', models.CharField(max_length=255)),
                ('tradekey', models.CharField(max_length=255)),
                ('default', models.BooleanField(default=False)),
                ('user', models.ForeignKey(related_name='credential', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='CryptsyTransaction',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('amount', models.PositiveIntegerField()),
                ('fee', models.PositiveIntegerField()),
                ('timestamp', models.PositiveIntegerField()),
                ('timezone', models.CharField(max_length=3)),
                ('trxid', models.CharField(max_length=255, null=True, blank=True)),
                ('message', models.CharField(max_length=255)),
                ('datetime', models.DateTimeField()),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('matched_on', models.DateTimeField(null=True, blank=True)),
                ('completed_on', models.DateTimeField(null=True, blank=True)),
                ('address', models.ForeignKey(related_name='cryptsy_transaction', to='payments.CoinAddress')),
                ('comment', models.ForeignKey(related_name='cryptsy_transaction', to='core.Comment')),
                ('sender_credential', models.ForeignKey(related_name='cryptsy_transaction', to='payments.CryptsyCredential')),
            ],
        ),
        migrations.CreateModel(
            name='PayPalTransaction',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('payKey', models.CharField(max_length=255)),
                ('paymentExecStatus', models.CharField(max_length=255, choices=[(b'CREATED', b'Created'), (b'COMPLETED', b'Completed'), (b'INCOMPLETE', b'Incomplete'), (b'ERROR', b'Error'), (b'REVERSALERROR', b'Reversalerror')])),
                ('currency', models.CharField(max_length=3)),
                ('created_at', models.DateTimeField(auto_now=True)),
                ('amount', models.DecimalField(max_digits=16, decimal_places=2)),
                ('hours', models.DecimalField(default=0, max_digits=20, decimal_places=8)),
                ('hours_matched', models.DecimalField(default=0.0, max_digits=20, decimal_places=8)),
                ('comment', models.ForeignKey(related_name='paypal_transaction', to='core.Comment')),
                ('receiver_user', models.ForeignKey(related_name='receiver_user_transaction', blank=True, to=settings.AUTH_USER_MODEL, null=True)),
                ('sender_user', models.ForeignKey(related_name='sender_user_transaction', blank=True, to=settings.AUTH_USER_MODEL, null=True)),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='coinaddress',
            unique_together=set([('currency_code', 'address')]),
        ),
    ]
