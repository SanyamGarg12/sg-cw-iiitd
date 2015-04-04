# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('studentportal', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Edit',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('diff_text', models.TextField(max_length=2000, blank=True)),
                ('when', models.DateTimeField(default=django.utils.timezone.now)),
                ('project', models.ForeignKey(related_name='edits', to='studentportal.Project')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
