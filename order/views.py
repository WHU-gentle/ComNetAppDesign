from django.forms import model_to_dict
from django.http import JsonResponse, Http404
from django.shortcuts import render

# Create your views here.
from book.models import Book
from user.models import Cart
from order.models import Order, OrderContent
from django.core import serializers

import datetime


def all(request):
    pass


def detail(request, order_id):
    content = {}
    # 订单本身的信息
    try:
        order = Order.objects.get(order_id=order_id)
    except Cart.DoesNotExist:
        return Http404
    except Cart.MultipleObjectsReturned:
        raise Exception('同一订单号出现多次')

    # object 转 dict
    content['order'] = model_to_dict(order)

    # 订单中书籍的信息
    content['order_content'] = []
    order_content = OrderContent.objects.filter(order_id=order_id)
    for book in order_content:
        element = {
            'id': book.book_id,
            'book_id': book.book_id,
            'number': book.number,
            'price': book.price,  # 此处是同种书的总价
        }
        try:
            book = Book.objects.get(book_id=book.book_id)
        except Cart.DoesNotExist:
            raise Exception('书编号%d不存在' % book.book_id)
        except Cart.MultipleObjectsReturned:
            raise Exception('书编号%d出现多次' % book.book_id)
        element.update({
            'book_name': book.book_name,
            'book_picture': book.book_picture,
            'author': book.author,
            'press': book.press,
            'kind_name': book.kind_name,
        })
        content['order_content'].append(element)
    # 因为没有对应前端，先返回成json
    return JsonResponse(content)



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
    for book in Cart.objects.filter(
            user_id=request.session['user']['user_id'],
            select=True,
    ).all():
        OrderContent.objects.create(
            order_id=order.order_id,
            book_id=book.book_id,
            number=book.number,
            price=book.price
        )
        sum_price += book.number * book.price
    Order.objects.filter(order_id=order.order_id).update(sum_price=sum_price)
    Cart.objects.filter(
        user_id=request.session['user']['user_id'],
        select=True,
    ).delete()
    # order.save()
    return JsonResponse({'res': 1})


def receive(request):
    order_id = request.GET.get('order_id')
    try:
        order = Order.objects.get(user_id=request.session['user']['user_id'], order_id=order_id)
    except Order.DoesNotExist:
        # 订单不存在
        return JsonResponse({'res': 0, 'errmsg': '订单不存在'})
    except Order.MultipleObjectsReturned:
        raise Exception('订单表错误')
    if order.status == 3:
        order.status = 4
        order.save()
        return JsonResponse({'res': 1})
    else:
        return JsonResponse({'res': 0, 'errmsg': '订单不可收货'})
