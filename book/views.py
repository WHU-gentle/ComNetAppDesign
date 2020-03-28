from django.http import JsonResponse
from django.shortcuts import render
from user.models import Cart
from book.models import Book


# Create your views here.


def detail(request, book_id):
    pass


def kind(request, kind_id):
    pass


def search(request, keyword):
    pass


# 用户将一本书加入购物车
def buy(request):
    book_id = request.GET.get('book_id')
    try:
        now = Cart.objects.get(user_id=request.session['user']['user_id'], book_id=book_id)
    except Cart.DoesNotExist:
        # 之前不存在，加入
        try:
            book = Book.objects.get(book_id=book_id)
        except Exception:
            return JsonResponse({'res': 0, 'errmsg': '不存在的商品'})

        Cart.objects.create(
            user_id=request.session['user']['user_id'],
            book_id=book_id,
            number=1,
            price=book.price,
        )
    except Cart.MultipleObjectsReturned:
        # 购物车表中
        raise Exception('购物车中同一商品出现多次')
    else:
        # 之前存在,数量+1
        Cart.objects.filter(user_id=request.session['user']['user_id'], book_id=book_id).update(number=now.number+1)
    return JsonResponse({'res': 1})