from django.contrib.auth.models import AbstractBaseUser, UserManager
from django.db import models
from django.utils import timezone


class User(AbstractBaseUser):
    username = models.CharField('username', max_length=128, unique=True)
    first_name = models.CharField('first name', max_length=30, blank=True)
    last_name = models.CharField('last name', max_length=30, blank=True)
    email = models.EmailField('email address', blank=True)
    is_active = models.BooleanField('active', default=True)
    is_superuser = models.BooleanField('superuser status', default=False)
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
