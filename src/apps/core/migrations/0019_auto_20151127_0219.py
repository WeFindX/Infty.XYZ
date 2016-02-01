# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0018_auto_20151125_1532'),
    ]

    operations = [
        migrations.AddField(
            model_name='vote',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2015, 11, 27, 10, 19, 20, 934192, tzinfo=utc), auto_now_add=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='vote',
            name='updated_at',
            field=models.DateTimeField(default=datetime.datetime(2015, 11, 27, 10, 19, 24, 374760, tzinfo=utc), auto_now=True),
            preserve_default=False,
        ),
    ]
