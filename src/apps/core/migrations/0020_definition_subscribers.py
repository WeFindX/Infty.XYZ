# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('core', '0019_auto_20151127_0219'),
    ]

    operations = [
        migrations.AddField(
            model_name='definition',
            name='subscribers',
            field=models.ManyToManyField(related_name='definition_subscribers', to=settings.AUTH_USER_MODEL, blank=True),
        ),
    ]
