# -*- coding: utf-8 -*-


from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='goal',
            name='sharewith',
            field=models.ManyToManyField(to=settings.AUTH_USER_MODEL, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='idea',
            name='sharewith',
            field=models.ManyToManyField(to=settings.AUTH_USER_MODEL, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='need',
            name='sharewith',
            field=models.ManyToManyField(to=settings.AUTH_USER_MODEL, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='plan',
            name='sharewith',
            field=models.ManyToManyField(to=settings.AUTH_USER_MODEL, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='step',
            name='sharewith',
            field=models.ManyToManyField(to=settings.AUTH_USER_MODEL, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='task',
            name='sharewith',
            field=models.ManyToManyField(to=settings.AUTH_USER_MODEL, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='work',
            name='sharewith',
            field=models.ManyToManyField(to=settings.AUTH_USER_MODEL, null=True, blank=True),
        ),
    ]
