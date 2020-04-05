from django.db import models

import datetime
from django.utils import timezone
# Create your models here.


# TODO 提供成员函数检查取值合法性
# TODO 数据库字段类型
class User(models.Model):
    def __str__(self):
        return self.user_name
    user_id = models.AutoField(primary_key = True)
    user_name = models.CharField(max_length=16, unique=True)
    password = models.CharField(max_length=16)
    phone_number = models.CharField(max_length=20)  # +86 0311 86012345
    address = models.CharField(max_length=100)
    email = models.CharField(max_length=50, unique=True)
    register_date = models.DateField()


class Cart(models.Model):
    def __str__(self):
        return str(self.user_id) + '的购物车'
    user_id = models.IntegerField()
    book_id = models.IntegerField()
    number = models.IntegerField(default=1)
    price = models.FloatField()
