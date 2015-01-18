import math
import uuid

from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser, UserManager
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.db import models
from django.db import IntegrityError
from django.utils import timezone
from django.utils.http import urlencode


class User(AbstractBaseUser):
    username = models.CharField('username', max_length=128, unique=True)
    first_name = models.CharField('first name', max_length=30, blank=True)
    last_name = models.CharField('last name', max_length=30, blank=True)
    email = models.EmailField('email address', blank=True)
    is_active = models.BooleanField('active', default=True)
    is_superuser = models.BooleanField('superuser status', default=False)
    is_staff = models.BooleanField('staff status', default=False)
    date_joined = models.DateTimeField('date joined', default=timezone.now)

    objects = UserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    class Meta:
        app_label = 'simpleoncall'
        db_table = 'auth_user'
        verbose_name = 'user'
        verbose_name_plural = 'users'

    def save(self, *args, **kwargs):
        if not self.username:
            self.username = self.email
        return super(User, self).save(*args, **kwargs)

    def get_full_name(self):
        return '%s %s' % (self.first_name, self.last_name)

    def get_short_name(self):
        return self.username

    def get_display_name(self):
        if self.first_name and self.last_name:
            return self.get_full_name()
        return self.get_short_name()

    def has_perm(self, perm_name):
        return self.is_superuser

    def has_module_perms(self, app_label):
        return self.is_superuser

    def get_alert_settings(self):
        return AlertSetting.objects.filter(user=self)


class TeamMember(models.Model):
    team = models.ForeignKey('simpleoncall.Team', related_name='team_set')
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, related_name='team_user_set'
    )
    email = models.EmailField(null=True, blank=True)
    date_added = models.DateTimeField(default=timezone.now)

    class Meta:
        app_label = 'simpleoncall'
        db_table = 'team_member'
        unique_together = (('team', 'user'), ('team', 'email'))


class Team(models.Model):
    name = models.CharField('name', max_length=128)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL)
    date_added = models.DateTimeField(default=timezone.now)
    users = models.ManyToManyField(
        settings.AUTH_USER_MODEL, through='simpleoncall.TeamMember', related_name='team_users'
    )

    class Meta:
        app_label = 'simpleoncall'
        db_table = 'team'

    def get_schedules(self):
        return TeamSchedule.objects.filter(team=self)

    def get_active_schedule(self):
        try:
            return TeamSchedule.objects.get(team=self, is_active=True)
        except ObjectDoesNotExist:
            return None


class APIKey(models.Model):
    team = models.ForeignKey('simpleoncall.Team')
    name = models.CharField('name', max_length=128)
    username = models.CharField('username', max_length=128)
    password = models.CharField('password', max_length=128)
    is_active = models.BooleanField('active status', default=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL)
    date_added = models.DateTimeField(default=timezone.now)

    class Meta:
        app_label = 'simpleoncall'
        db_table = 'api_key'
        unique_together = (('username', 'password'), )

    def get_name(self):
        return self.name or self.username

    def get_random_hash(self):
        return uuid.uuid4().hex

    def get_api_url(self):
        return '%s:%s@%s/api/' % (self.username, self.password, settings.BASE_URL)

    def save(self):
        if not self.username:
            self.username = self.get_random_hash()
        if not self.password:
            self.password = self.get_random_hash()

        return super(APIKey, self).save()


class TeamInvite(models.Model):
    team = models.ForeignKey('simpleoncall.Team')
    email = models.EmailField('email')
    invite_code = models.CharField('invite_code', max_length=64)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL)
    date_added = models.DateTimeField(default=timezone.now)

    class Meta:
        app_label = 'simpleoncall'
        db_table = 'team_invite'
        unique_together = (('email', 'team'), )

    def get_invite_url(self):
        query_string = {
            'code': self.invite_code,
            'email': self.email
        }
        return 'http://%s%s?%s' % (settings.BASE_URL, reverse('invite-accept'), urlencode(query_string))

    def save(self):
        if not self.invite_code:
            self.invite_code = uuid.uuid4().hex

        return super(TeamInvite, self).save()


class EventStatus:
    OPEN = 'open'
    RESOLVED = 'resolved'
    ACKNOWLEDGED = 'acknowledged'

    STATUSES = (
        (OPEN, OPEN),
        (RESOLVED, RESOLVED),
        (ACKNOWLEDGED, ACKNOWLEDGED),
    )


class Alert(models.Model):
    team = models.ForeignKey('simpleoncall.team')
    title = models.CharField('title', max_length=128)
    body = models.TextField('body', null=True, blank=True)
    status = models.CharField(
        'status', choices=EventStatus.STATUSES, null=False, blank=False,
        default=EventStatus.OPEN, max_length=24
    )
    created_by_api_key = models.ForeignKey('simpleoncall.APIKey', null=True, related_name='created_by_api_key')
    date_added = models.DateTimeField(default=timezone.now)

    updated_by_user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, related_name='updated_by_user')
    updated_by_api_key = models.ForeignKey('simpleoncall.APIKey', null=True, related_name='updated_by_api_key')
    date_updated = models.DateTimeField(default=timezone.now)

    class Meta:
        app_label = 'simpleoncall'
        db_table = 'alert'

    def save(self, user=None, api_key=None):
        if self.status not in EventStatus.STATUSES:
            raise IntegrityError('Invalid Alert status %r' % (self.status, ))
        self.updated_by_api_key = api_key
        self.updated_by_user = user
        self.date_updated = timezone.now()
        super(Alert, self).save()

    def get_body(self):
        return self.body or 'No Body'

    def last_updater(self):
        if self.updated_by_user:
            return self.updated_by_user.email
        elif self.updated_by_api_key:
            return self.updated_by_api_key.get_name()
        elif self.created_by_api_key:
            return self.created_by_api_key.get_name()
        return 'Unknown'

    def to_dict(self):
        data = {
            'title': self.title,
            'body': self.body,
            'status': self.status,
            'created': self.date_added.isoformat(),
            'created_by': self.created_by_api_key.get_name(),
            'updated': self.date_updated.isoformat(),
            'updated_by': self.last_updater(),
        }

        return data


class TeamSchedule(models.Model):
    team = models.ForeignKey('simpleoncall.team')
    name = models.CharField('name', max_length=128)
    starting_time = models.IntegerField('starting_time', default=9)
    rotation_duration = models.IntegerField('rotation_duration', default=7)
    users = models.ManyToManyField(
        settings.AUTH_USER_MODEL, related_name='schedule_users'
    )
    start_date = models.DateTimeField(default=timezone.now)
    date_added = models.DateTimeField(default=timezone.now)
    is_active = models.BooleanField('active', default=False)

    class Meta:
        app_label = 'simpleoncall'
        db_table = 'team_schedule'
        unique_together = (('team', 'name'), )

    def get_currently_on_call(self, now=None):
        now = now or timezone.now()
        offset = (now - self.start_date).days
        offset = int(math.floor(offset / self.rotation_duration))
        index = offset % self.users.count()
        return self.users.all()[index]

    def save(self):
        if self.is_active:
            active_schedules = TeamSchedule.objects.filter(team=self.team, is_active=True)
            for schedule in active_schedules:
                schedule.is_active = False
                schedule.save()
        super(TeamSchedule, self).save()


class AlertType:
    EMAIL = 'email'
    SMS = 'sms'
    VOICE = 'voice'

    TYPES = (
        (EMAIL, EMAIL),
        (SMS, SMS),
        (VOICE, VOICE),
    )


class AlertSetting(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    type = models.CharField(
        'type', choices=AlertType.TYPES, null=False, blank=False,
        default=AlertType.EMAIL, max_length=24
    )
    time = models.IntegerField('time', null=False, blank=False, default=0)
    date_added = models.DateTimeField(default=timezone.now)
    date_updated = models.DateTimeField(default=timezone.now)

    class Meta:
        app_label = 'simpleoncall'
        db_table = 'alert_setting'
        unique_together = (('type', 'time'), )

    def save(self):
        self.date_updated = timezone.now()
        super(AlertSetting, self).save()
