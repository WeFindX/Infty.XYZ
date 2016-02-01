# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_translation'),
    ]

    operations = [
        migrations.AddField(
            model_name='language',
            name='language_code',
            field=models.CharField(default='', max_length=4),
            preserve_default=False,
        ),
    ]
