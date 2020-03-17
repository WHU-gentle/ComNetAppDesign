from django.db import models

# Create your models here.


class Order(models.Model):
    def __str__(self):
        return self.book_name

    order_id = models.AutoField(primary_key=True)
    user_id = models.IntegerField()
    date = models.CharField(max_length=10)  # 2020-03-17
    time = models.CharField(max_length=5)  # 16:11
    sum_price = models.FloatField()
    status = models.CharField(max_length=16)  # TODO IntegerField ?


class OrderContent(models.Model):
    def __str__(self):
        return self.book_name

    order_id = models.IntegerField()
    book_id = models.IntegerField()
    number = models.IntegerField()
    price = models.FloatField()