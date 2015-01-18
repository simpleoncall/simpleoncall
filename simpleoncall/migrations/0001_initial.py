# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone
from django.conf import settings


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
                ('is_staff', models.BooleanField(default=False, verbose_name=b'staff status')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name=b'date joined')),
            ],
            options={
                'db_table': 'auth_user',
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Alert',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=128, verbose_name=b'title')),
                ('body', models.TextField(null=True, verbose_name=b'body', blank=True)),
                ('status', models.CharField(default=b'open', max_length=24, verbose_name=b'status', choices=[(b'open', b'open'), (b'resolved', b'resolved'), (b'acknowledged', b'acknowledged')])),
                ('date_added', models.DateTimeField(default=django.utils.timezone.now)),
                ('date_updated', models.DateTimeField(default=django.utils.timezone.now)),
            ],
            options={
                'db_table': 'alert',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='AlertSetting',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('type', models.CharField(default=b'email', max_length=24, verbose_name=b'type', choices=[(b'email', b'email'), (b'sms', b'sms'), (b'voice', b'voice')])),
                ('time', models.IntegerField(default=0, verbose_name=b'time')),
                ('date_added', models.DateTimeField(default=django.utils.timezone.now)),
                ('date_updated', models.DateTimeField(default=django.utils.timezone.now)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'alert_setting',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='APIKey',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=128, verbose_name=b'name')),
                ('username', models.CharField(max_length=128, verbose_name=b'username')),
                ('password', models.CharField(max_length=128, verbose_name=b'password')),
                ('is_active', models.BooleanField(default=True, verbose_name=b'active status')),
                ('date_added', models.DateTimeField(default=django.utils.timezone.now)),
                ('created_by', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'api_key',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Team',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=128, verbose_name=b'name')),
                ('date_added', models.DateTimeField(default=django.utils.timezone.now)),
                ('owner', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'team',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='TeamInvite',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('email', models.EmailField(max_length=75, verbose_name=b'email')),
                ('invite_code', models.CharField(max_length=64, verbose_name=b'invite_code')),
                ('date_added', models.DateTimeField(default=django.utils.timezone.now)),
                ('created_by', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
                ('team', models.ForeignKey(to='simpleoncall.Team')),
            ],
            options={
                'db_table': 'team_invite',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='TeamMember',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('email', models.EmailField(max_length=75, null=True, blank=True)),
                ('date_added', models.DateTimeField(default=django.utils.timezone.now)),
                ('team', models.ForeignKey(related_name='team_set', to='simpleoncall.Team')),
                ('user', models.ForeignKey(related_name='team_user_set', blank=True, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'db_table': 'team_member',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='TeamSchedule',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=128, verbose_name=b'name')),
                ('starting_time', models.IntegerField(default=9, verbose_name=b'starting_time')),
                ('rotation_duration', models.IntegerField(default=7, verbose_name=b'rotation_duration')),
                ('start_date', models.DateTimeField(default=django.utils.timezone.now)),
                ('date_added', models.DateTimeField(default=django.utils.timezone.now)),
                ('is_active', models.BooleanField(default=False, verbose_name=b'active')),
                ('team', models.ForeignKey(to='simpleoncall.Team')),
                ('users', models.ManyToManyField(related_name='schedule_users', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'team_schedule',
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='teamschedule',
            unique_together=set([('team', 'name')]),
        ),
        migrations.AlterUniqueTogether(
            name='teammember',
            unique_together=set([('team', 'user'), ('team', 'email')]),
        ),
        migrations.AlterUniqueTogether(
            name='teaminvite',
            unique_together=set([('email', 'team')]),
        ),
        migrations.AddField(
            model_name='team',
            name='users',
            field=models.ManyToManyField(related_name='team_users', through='simpleoncall.TeamMember', to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='apikey',
            name='team',
            field=models.ForeignKey(to='simpleoncall.Team'),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='apikey',
            unique_together=set([('username', 'password')]),
        ),
        migrations.AlterUniqueTogether(
            name='alertsetting',
            unique_together=set([('type', 'time')]),
        ),
        migrations.AddField(
            model_name='alert',
            name='created_by_api_key',
            field=models.ForeignKey(related_name='created_by_api_key', to='simpleoncall.APIKey', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='alert',
            name='team',
            field=models.ForeignKey(to='simpleoncall.Team'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='alert',
            name='updated_by_api_key',
            field=models.ForeignKey(related_name='updated_by_api_key', to='simpleoncall.APIKey', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='alert',
            name='updated_by_user',
            field=models.ForeignKey(related_name='updated_by_user', to=settings.AUTH_USER_MODEL, null=True),
            preserve_default=True,
        ),
    ]
