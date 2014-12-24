# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(default=django.utils.timezone.now, verbose_name='last login')),
                ('username', models.CharField(unique=True, max_length=128, verbose_name=b'username')),
                ('first_name', models.CharField(max_length=30, verbose_name=b'first name', blank=True)),
                ('last_name', models.CharField(max_length=30, verbose_name=b'last name', blank=True)),
                ('email', models.EmailField(max_length=75, verbose_name=b'email address', blank=True)),
                ('is_active', models.BooleanField(default=True, verbose_name=b'active')),
                ('is_superuser', models.BooleanField(default=False, verbose_name=b'superuser status')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name=b'date joined')),
            ],
            options={
                'db_table': 'auth_user',
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
            },
            bases=(models.Model,),
        ),
    ]
