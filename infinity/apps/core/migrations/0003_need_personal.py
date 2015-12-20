# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_auto_20151008_0504'),
    ]

    operations = [
        migrations.AddField(
            model_name='need',
            name='personal',
            field=models.BooleanField(default=False),
        ),
    ]
