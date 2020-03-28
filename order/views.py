from django.http import JsonResponse
from django.shortcuts import render

# Create your views here.
from user.models import Cart
from order.models import Order, OrderContent

import datetime

def all(request):
    pass


def detail(request, order_id):
    pass


'''
    order_id = models.AutoField(primary_key=True)
    user_id = models.IntegerField()
    sum_price = models.FloatField()
    # 订单状态：已取消 0， 待付款 1， 待发货 2， 已发货 3， 已完成 4
    status = models.IntegerField()  # TODO IntegerField ?
    time_submit = models.DateTimeField()
    time_pay = models.DateTimeField()
    time_finish = models.DateTimeField()
    
    order_id = models.IntegerField()
    book_id = models.IntegerField()
    number = models.IntegerField()
    price = models.FloatField()
'''
# 创建订单
def new(request):
    order = Order(
        # order_id =
        user_id=request.session['user']['user_id'],
        sum_price=0,
        # 订单状态：已取消 0， 待付款 1， 待发货 2， 已发货 3， 已完成 4
        status=1,
        time_submit=datetime.datetime.now(),
        # time_pay=None,
        # time_finish=None,
    )
    order.save()

    print(order.order_id)

    sum_price = 0.0
    for book in Cart.objects.filter(user_id=request.session['user']['user_id']).all():
        OrderContent.objects.create(
            order_id=order.order_id,
            book_id=book.book_id,
            number=book.number,
            price=book.price
        )
        sum_price += book.number * book.price
    Order.objects.filter(order_id=order.order_id).update(sum_price=sum_price)
    Cart.objects.filter(user_id=request.session['user']['user_id']).delete()
    # order.save()
    return JsonResponse({'res': 1})
