# -*- coding: utf-8 -*-


from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('core', '0010_auto_20151113_0443'),
    ]

    operations = [
        migrations.CreateModel(
            name='Definition',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('commented_at', models.DateTimeField(auto_now_add=True)),
                ('defined_meaning_id', models.PositiveIntegerField(null=True, blank=True)),
                ('definition', models.TextField()),
                ('personal', models.BooleanField(default=False)),
                ('name', models.TextField()),
                ('hours_donated', models.DecimalField(default=0.0, max_digits=20, decimal_places=8)),
                ('hours_claimed', models.DecimalField(default=0.0, max_digits=20, decimal_places=8)),
                ('hours_assumed', models.DecimalField(default=0.0, max_digits=20, decimal_places=8)),
                ('hours_matched', models.DecimalField(default=0.0, max_digits=20, decimal_places=8)),
                ('total_donated', models.DecimalField(default=0.0, max_digits=20, decimal_places=8)),
                ('total_claimed', models.DecimalField(default=0.0, max_digits=20, decimal_places=8)),
                ('total_assumed', models.DecimalField(default=0.0, max_digits=20, decimal_places=8)),
                ('total_matched', models.DecimalField(default=0.0, max_digits=20, decimal_places=8)),
                ('language', models.ForeignKey(blank=True, to='core.Language', null=True)),
                ('sharewith', models.ManyToManyField(to=settings.AUTH_USER_MODEL, null=True, blank=True)),
                ('type', models.ForeignKey(blank=True, to='core.Type', null=True)),
                ('user', models.ForeignKey(related_name='user_definitions', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='need',
            unique_together=set([]),
        ),
        migrations.RemoveField(
            model_name='need',
            name='language',
        ),
        migrations.RemoveField(
            model_name='need',
            name='sharewith',
        ),
        migrations.RemoveField(
            model_name='need',
            name='type',
        ),
        migrations.RemoveField(
            model_name='need',
            name='user',
        ),
        migrations.DeleteModel(
            name='Need',
        ),
        migrations.AddField(
            model_name='goal',
            name='definition',
            field=models.ForeignKey(blank=True, to='core.Definition', null=True),
        ),
        migrations.AlterUniqueTogether(
            name='definition',
            unique_together=set([('language', 'name', 'definition')]),
        ),
    ]
