from django.contrib import admin

# Register your models here.
from .models import Order
from .models import OrderContent


class OrderAdmin(admin.ModelAdmin):
    fields = [
        # 'order_id',
        'user_id',
        'sum_price',
        # 订单状态：已取消 0， 待付款 1， 待发货 2， 已发货 3， 已完成 4
        'status',
        'time_submit',
        'time_pay',
        'time_finish',
    ]


class OrderContentAdmin(admin.ModelAdmin):
    fields = [
        'order_id',
        'book_id',
        'number',
        'price',
    ]


admin.site.register(Order, OrderAdmin)
admin.site.register(OrderContent, OrderContentAdmin)
