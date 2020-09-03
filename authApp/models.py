from django.db import models
from django.contrib.auth.models import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

from .managers import CustomUserManager


class Facility(models.Model):
    mfl_code = models.PositiveIntegerField()
    name = models.CharField(max_length=80)
    county = models.CharField(max_length=30)
    sub_county = models.CharField(max_length=80)

    def __str__(self):
        return self.name

    class Meta:
        db_table = "Facilities"


class Designation(models.Model):
    name = models.CharField(max_length=80)

    def __str__(self):
        return self.name

    class Meta:
        db_table = "Designations"


class Users(AbstractBaseUser, PermissionsMixin):
    f_name = models.CharField(max_length=50, unique=False)
    l_name = models.CharField(max_length=50, unique=False)
    designation = models.ForeignKey(Designation, on_delete=models.CASCADE)
    facility = models.ForeignKey(Facility, on_delete=models.CASCADE)
    email = models.EmailField(_('email address'), unique=True)
    msisdn = models.CharField(max_length=15, unique=True)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(default=timezone.now)

    USERNAME_FIELD = 'msisdn'
    REQUIRED_FIELDS = ['designation', 'facility', 'email', 'f_name', 'l_name']

    objects = CustomUserManager()

    def __str__(self):
        return self.msisdn

    class Meta:
        db_table = "User"
