from django.db import models

# Create your models here.


class Order(models.Model):
    def __str__(self):
        return str(self.order_id)

    order_id = models.AutoField(primary_key=True)
    user_id = models.IntegerField()
    sum_price = models.FloatField()
    # 订单状态：已取消 0， 待付款 1， 待发货 2， 已发货 3， 已完成 4
    status = models.IntegerField()
    time_submit = models.DateTimeField()
    time_pay = models.DateTimeField(null=True)
    time_finish = models.DateTimeField(null=True)


class OrderContent(models.Model):
    def __str__(self):
        return str(self.book_id)

    order_id = models.IntegerField()
    book_id = models.IntegerField()
    number = models.IntegerField()
    price = models.FloatField()
