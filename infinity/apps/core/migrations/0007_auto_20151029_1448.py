# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0006_auto_20151021_0429'),
    ]

    operations = [
        migrations.AlterField(
            model_name='idea',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AlterField(
            model_name='plan',
            name='name',
            field=models.CharField(max_length=150),
        ),
        migrations.AlterField(
            model_name='plan',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AlterField(
            model_name='step',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AlterField(
            model_name='task',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AlterField(
            model_name='work',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
