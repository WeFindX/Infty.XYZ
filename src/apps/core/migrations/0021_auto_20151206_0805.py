# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0020_definition_subscribers'),
    ]

    operations = [
        migrations.AddField(
            model_name='goal',
            name='is_historical',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='idea',
            name='is_historical',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='need',
            name='is_historical',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='plan',
            name='is_historical',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='step',
            name='is_historical',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='task',
            name='is_historical',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='work',
            name='is_historical',
            field=models.BooleanField(default=False),
        ),
    ]
