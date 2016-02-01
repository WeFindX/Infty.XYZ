# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
import django_markdown.models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('core', '0011_auto_20151113_0555'),
    ]

    operations = [
        migrations.CreateModel(
            name='Need',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('commented_at', models.DateTimeField(auto_now_add=True)),
                ('hours_donated', models.DecimalField(default=0.0, max_digits=20, decimal_places=8)),
                ('hours_claimed', models.DecimalField(default=0.0, max_digits=20, decimal_places=8)),
                ('hours_assumed', models.DecimalField(default=0.0, max_digits=20, decimal_places=8)),
                ('hours_matched', models.DecimalField(default=0.0, max_digits=20, decimal_places=8)),
                ('name', models.CharField(max_length=150)),
                ('personal', models.BooleanField(default=False)),
                ('total_donated', models.DecimalField(default=0.0, max_digits=20, decimal_places=8)),
                ('total_claimed', models.DecimalField(default=0.0, max_digits=20, decimal_places=8)),
                ('total_assumed', models.DecimalField(default=0.0, max_digits=20, decimal_places=8)),
                ('total_matched', models.DecimalField(default=0.0, max_digits=20, decimal_places=8)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('content', django_markdown.models.MarkdownField()),
                ('definition', models.ForeignKey(to='core.Definition')),
                ('language', models.ForeignKey(blank=True, to='core.Language', null=True)),
                ('sharewith', models.ManyToManyField(to=settings.AUTH_USER_MODEL, blank=True)),
                ('user', models.ForeignKey(related_name='user_needs', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
