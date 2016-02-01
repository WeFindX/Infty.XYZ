# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('core', '0016_auto_20151119_1644'),
    ]

    operations = [
        migrations.AddField(
            model_name='goal',
            name='subscribers',
            field=models.ManyToManyField(related_name='goal_subscribers', to=settings.AUTH_USER_MODEL, blank=True),
        ),
        migrations.AddField(
            model_name='idea',
            name='subscribers',
            field=models.ManyToManyField(related_name='idea_subscribers', to=settings.AUTH_USER_MODEL, blank=True),
        ),
        migrations.AddField(
            model_name='need',
            name='subscribers',
            field=models.ManyToManyField(related_name='need_subscribers', to=settings.AUTH_USER_MODEL, blank=True),
        ),
        migrations.AddField(
            model_name='plan',
            name='subscribers',
            field=models.ManyToManyField(related_name='plan_subscribers', to=settings.AUTH_USER_MODEL, blank=True),
        ),
        migrations.AddField(
            model_name='step',
            name='subscribers',
            field=models.ManyToManyField(related_name='step_subscribers', to=settings.AUTH_USER_MODEL, blank=True),
        ),
        migrations.AddField(
            model_name='task',
            name='subscribers',
            field=models.ManyToManyField(related_name='task_subscribers', to=settings.AUTH_USER_MODEL, blank=True),
        ),
        migrations.AddField(
            model_name='work',
            name='subscribers',
            field=models.ManyToManyField(related_name='work_subscribers', to=settings.AUTH_USER_MODEL, blank=True),
        ),
    ]
