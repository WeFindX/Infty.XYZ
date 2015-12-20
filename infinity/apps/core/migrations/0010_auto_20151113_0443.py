# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0009_merge'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='goal',
            name='languages',
        ),
        migrations.RemoveField(
            model_name='goal',
            name='need',
        ),
        migrations.RemoveField(
            model_name='idea',
            name='languages',
        ),
        migrations.RemoveField(
            model_name='plan',
            name='languages',
        ),
        migrations.RemoveField(
            model_name='step',
            name='languages',
        ),
        migrations.RemoveField(
            model_name='task',
            name='languages',
        ),
        migrations.RemoveField(
            model_name='work',
            name='languages',
        ),
    ]
