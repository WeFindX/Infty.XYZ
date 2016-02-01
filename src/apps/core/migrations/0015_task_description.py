# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django_markdown.models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0014_auto_20151119_0221'),
    ]

    operations = [
        migrations.AddField(
            model_name='task',
            name='description',
            field=django_markdown.models.MarkdownField(default=''),
            preserve_default=False,
        ),
    ]
