# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('studentportal', '__first__'),
    ]

    operations = [
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('text', models.CharField(max_length=200)),
                ('commentor', models.ForeignKey(related_name='comments', to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Diff',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('diff_type', models.IntegerField(max_length=12)),
                ('details', models.TextField(max_length=1000, null=True)),
                ('when', models.DateTimeField(default=django.utils.timezone.now)),
                ('person', models.ForeignKey(related_name='diff', to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Example',
            fields=[
                ('project', models.OneToOneField(primary_key=True, serialize=False, to='studentportal.Project')),
                ('date_created', models.DateTimeField(default=django.utils.timezone.now)),
                ('likes_count', models.IntegerField(default=0)),
                ('comments_count', models.IntegerField(default=0)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Like',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('liked_by', models.ForeignKey(related_name='liked_projects', to=settings.AUTH_USER_MODEL)),
                ('project', models.ForeignKey(related_name='likes', to='supervisor.Example')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='News',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('content', models.TextField(max_length=1000)),
                ('date_created', models.DateTimeField(default=django.utils.timezone.now)),
                ('priority', models.BooleanField(default=False)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('noti_type', models.IntegerField(max_length=5, null=True, blank=True)),
                ('NGO_name', models.CharField(max_length=200, blank=True)),
                ('NGO_link', models.URLField(blank=True)),
                ('NGO_details', models.TextField(blank=True)),
                ('NGO_sugg_by', models.ForeignKey(to=settings.AUTH_USER_MODEL, null=True)),
                ('project', models.ForeignKey(to='studentportal.Project', null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='TA',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('email', models.CharField(max_length=100)),
                ('instructor', models.BooleanField(default=False)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='diff',
            name='project',
            field=models.ForeignKey(related_name='diff', to='studentportal.Project', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='comment',
            name='project',
            field=models.ForeignKey(related_name='comments', to='supervisor.Example'),
            preserve_default=True,
        ),
    ]
