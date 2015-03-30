# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import studentportal.validators
import django.db.models.deletion
import studentportal.decorators
import django.utils.timezone
from django.conf import settings
import studentportal.models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Bug',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('suggestions', models.TextField(max_length=2000, blank=True)),
                ('rating', models.IntegerField()),
                ('user', models.ForeignKey(related_name='bugs', to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=300)),
                ('description', models.CharField(max_length=1000, blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Document',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('document', models.FileField(upload_to=studentportal.decorators._PathAndRename(b'uploads/%Y/'))),
                ('name', models.CharField(max_length=100)),
                ('date_added', models.DateTimeField(default=django.utils.timezone.now)),
                ('category', models.IntegerField(max_length=5)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='NGO',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=1000)),
                ('link', models.URLField(blank=True)),
                ('details', models.TextField(blank=True)),
                ('category', models.ForeignKey(related_name='NGOs', on_delete=models.SET(studentportal.models._get_other_category), to='studentportal.Category', null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Project',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=1000)),
                ('date_created', models.DateTimeField(default=django.utils.timezone.now)),
                ('credits', models.IntegerField(default=2, validators=[studentportal.validators.validate_credits])),
                ('NGO_name', models.CharField(max_length=1000)),
                ('NGO_details', models.CharField(max_length=1000)),
                ('NGO_super', models.CharField(max_length=1000)),
                ('NGO_super_contact', models.CharField(max_length=100)),
                ('goals', models.TextField()),
                ('schedule_text', models.TextField()),
                ('finish_date', models.DateTimeField(null=True, blank=True)),
                ('stage', models.IntegerField(default=1, max_length=5)),
                ('deleted', models.BooleanField(default=False)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Feedback',
            fields=[
                ('project', models.ForeignKey(related_name='feedback', primary_key=True, serialize=False, to='studentportal.Project')),
                ('hours', models.IntegerField(validators=[studentportal.validators.validate_feedback_hours])),
                ('achievements', models.TextField(max_length=2000)),
                ('experience', models.IntegerField(default=1, choices=[(1, b'Very Poor'), (2, b'Poor'), (3, b'Neutral'), (4, b'Good'), (5, b'Very Good')])),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='project',
            name='NGO',
            field=models.ForeignKey(related_name='projects', on_delete=django.db.models.deletion.SET_NULL, blank=True, to='studentportal.NGO', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='project',
            name='category',
            field=models.ForeignKey(related_name='projects', on_delete=models.SET(studentportal.models._get_other_category), to='studentportal.Category'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='project',
            name='student',
            field=models.ForeignKey(related_name='projects', to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='document',
            name='project',
            field=models.ForeignKey(related_name='documents', to='studentportal.Project'),
            preserve_default=True,
        ),
    ]
