# -*- coding: utf-8 -*-


from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('core', '0017_auto_20151121_1633'),
    ]

    operations = [
        migrations.CreateModel(
            name='Vote',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('value', models.IntegerField(choices=[(1, b'Positive'), (0, b'Neural'), (-1, b'Negative')])),
                ('comment', models.ForeignKey(related_name='vote_comment', to='core.Comment')),
                ('user', models.ForeignKey(related_name='vote_user', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='vote',
            unique_together=set([('user', 'comment')]),
        ),
    ]
