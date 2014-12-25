import uuid

from django.contrib.auth.models import AbstractBaseUser, UserManager
from django.db import models
from django.utils import timezone

from django.conf import settings


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

    def has_perm(self, perm_name):
        return self.is_superuser

    def has_module_perms(self, app_label):
        return self.is_superuser


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
