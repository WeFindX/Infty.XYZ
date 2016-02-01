# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0006_auto_20151021_0429'),
    ]

    operations = [
        migrations.AddField(
            model_name='goal',
            name='languages',
            field=models.ManyToManyField(related_name='goal_languages', null=True, to='core.Language', blank=True),
        ),
        migrations.AddField(
            model_name='idea',
            name='languages',
            field=models.ManyToManyField(related_name='idea_languages', null=True, to='core.Language', blank=True),
        ),
        migrations.AddField(
            model_name='plan',
            name='languages',
            field=models.ManyToManyField(related_name='plan_languages', null=True, to='core.Language', blank=True),
        ),
        migrations.AddField(
            model_name='step',
            name='languages',
            field=models.ManyToManyField(related_name='step_languages', null=True, to='core.Language', blank=True),
        ),
        migrations.AddField(
            model_name='task',
            name='languages',
            field=models.ManyToManyField(related_name='task_languages', null=True, to='core.Language', blank=True),
        ),
        migrations.AddField(
            model_name='work',
            name='languages',
            field=models.ManyToManyField(related_name='work_languages', null=True, to='core.Language', blank=True),
        ),
    ]
