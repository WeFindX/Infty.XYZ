# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0015_task_description'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='goal',
            name='definition',
        ),
        migrations.AddField(
            model_name='goal',
            name='need',
            field=models.ForeignKey(blank=True, to='core.Need', null=True),
        ),
    ]
