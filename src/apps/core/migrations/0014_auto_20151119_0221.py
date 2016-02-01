# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0013_translation_content'),
    ]

    operations = [
        migrations.AddField(
            model_name='goal',
            name='is_link',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='goal',
            name='url',
            field=models.URLField(max_length=150, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='idea',
            name='is_link',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='idea',
            name='url',
            field=models.URLField(max_length=150, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='need',
            name='is_link',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='need',
            name='url',
            field=models.URLField(max_length=150, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='plan',
            name='is_link',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='plan',
            name='url',
            field=models.URLField(max_length=150, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='step',
            name='is_link',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='step',
            name='url',
            field=models.URLField(max_length=150, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='task',
            name='is_link',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='task',
            name='url',
            field=models.URLField(max_length=150, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='work',
            name='is_link',
            field=models.BooleanField(default=False),
        ),
    ]
