from django.db import models

import datetime
from django.utils import timezone
# Create your models here.


class User(models.Model):
    def __str__(self):
        return self.user_name

    user_name = models.CharField(max_length=16, primary_key=True)
    password = models.CharField(max_length=16)
    phone_number = models.CharField(max_length=20)
    address = models.CharField(max_length=100)
    email = models.CharField(max_length=50)