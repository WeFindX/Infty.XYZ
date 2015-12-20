# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('core', '0003_need_personal'),
    ]

    operations = [
        migrations.CreateModel(
            name='Translation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.TextField(null=True, blank=True)),
                ('summary', models.TextField(null=True, blank=True)),
                ('description', models.TextField(null=True, blank=True)),
                ('reason', models.TextField(null=True, blank=True)),
                ('objective', models.TextField(null=True, blank=True)),
                ('situation', models.TextField(null=True, blank=True)),
                ('deliverable', models.TextField(null=True, blank=True)),
                ('investables', models.TextField(null=True, blank=True)),
                ('deliverables', models.TextField(null=True, blank=True)),
                ('object_id', models.PositiveIntegerField()),
                ('content_type', models.ForeignKey(to='contenttypes.ContentType')),
                ('language', models.ForeignKey(to='core.Language')),
            ],
        ),
    ]
