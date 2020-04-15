from django.http import JsonResponse
from django.shortcuts import render
from user.models import Cart
from book.models import Book
from django.http import HttpResponse, JsonResponse
from .models import Book
from order.models import Order, OrderContent
from order.views import detail as o_detail
from django.db.models import Q
import datetime

# Create your views here.


def detail(request, book_id):
    try:
        book = Book.objects.get(pk=book_id)
    except Book.DoesNotExist:
        return HttpResponse("你所访问的页面不存在", status=404)

    book_detail = {
        'id': book.book_id,
        'name': book.book_name,
        'picture': book.book_picture,
        'price': book.price,
        'price_old': book.price_old,
        'author': book.author,
        'isbn': book.isbn,
        'press': book.press,
        'rest': book.rest,
        'kind_name': book.kind_name,
        'kind_id': book.kind_id,
        'sales': book.sales,
        'description': book.description,
    }
    return render(request, 'book/detail.html', {'book': book_detail})


def kind(request, kind_id):
    bookList = Book.objects.filter(kind_id=kind_id)
    if len(bookList) == 0:
        return HttpResponse("你所访问的页面不存在", status=404)

    kind_name = bookList[0].kind_name
    books = []
    for book in bookList:
        book_detail = {
            'name': book.book_name,
            'picture': book.book_picture,
            'price': book.price,
            'price_old': book.price_old,
            'author': book.author,
            'press': book.press,
            'rest': book.rest,
            'sales': book.sales,
            'id': book.book_id
        }
        books.append(book_detail)
    return render(request, 'book/kind.html', {'books': books, 'kind_name': kind_name})

def search(request):
    keyword = request.POST.get('keyword')
    bookList = Book.objects.filter(Q(book_name__contains=keyword) | Q(author__contains=keyword) | Q(press__contains=keyword))\
                            .order_by('-sales')

    books = []
    for book in bookList:
        book_detail = {
            'id': book.book_id,
            'name': book.book_name,
            'picture': book.book_picture,
            'price': book.price,
            'price_old': book.price_old,
            'author': book.author,
            'press': book.press,
            'rest': book.rest,
            'sales': book.sales,
        }
        books.append(book_detail)
    return render(request, 'book/search.html', {'books': books})


# 用户将number本书加入购物车（缺省1本）
def buy(request):
    if request.method == 'POST':
        return JsonResponse({'res': 0, 'errmsg': '访问方式错误'})

    # 数字
    try:
        book_id = int(request.GET.get('book_id'))
        number = int(request.GET.get('number', 1))
    except ValueError:
        # 商品数目不合法
        return JsonResponse({'res': 0, 'errmsg': '商品数量必须为数字'})
    print(book_id)
    print(type(book_id))
    print(number)
    print(type(number))
    # 检查数据不为空
    if not all([book_id, number]):
        return JsonResponse({'res': 0, 'errmsg': '数据不完整'})
    # 检查商品存在
    book = Book.objects.get(book_id=book_id)
    if book is None:
        # 商品不存在
        return JsonResponse({'res': 0, 'errmsg': '商品不存在'})

    # 加入购物车
    try:
        now = Cart.objects.get(user_id=request.session['user']['user_id'], book_id=book_id)
    except Cart.DoesNotExist:
        # 之前不存在，加入
        Cart.objects.create(
            user_id=request.session['user']['user_id'],
            book_id=book_id,
            number=number,
            price=book.price,
            select=True,
        )
    except Cart.MultipleObjectsReturned:
        # 购物车表中出现多次 数据库错误
        raise Exception('购物车中同一商品出现多次')
    else:
        # 之前存在,数量+number
        Cart.objects.filter(user_id=request.session['user']['user_id'], book_id=book_id)\
            .update(number=now.number + number)
    return JsonResponse({'res': 1, 'msg':'您成功添加了'+str(number)+'本'+str(book.book_name)})

# 立即购买
def buynow(request):
    try:
        book_id = int(request.GET.get('book_id'))
        number = int(request.GET.get('number', 1))
    except ValueError:
        # 商品数目不合法
        return JsonResponse({'res': 0, 'errmsg': '商品数量必须为数字'})
    book = Book.objects.get(book_id=book_id)

    order = Order(
        user_id=request.session['user']['user_id'],
        sum_price=int(number)*int(book.price),
        # 订单状态：已取消 0， 待付款 1， 待发货 2， 已发货 3， 已完成 4
        status=1,
        time_submit=datetime.datetime.now()
    )
    order.save()

    OrderContent.objects.create(
        order_id=order.order_id,
        book_id=book_id,
        number=number,
        price=book.price
    )

    return o_detail(request, order.order_id)
    

# 删除用户购物车中商品的信息
def cancel(request):
    try:
        book_id = int(request.GET.get('book_id'))
    except ValueError:
        return JsonResponse({'res': 0, 'errmsg': '参数错误'})

    try:
        now = Cart.objects.get(user_id=request.session['user']['user_id'], book_id=book_id)
    except Cart.DoesNotExist:
        # 之前不存在
        return JsonResponse({'res': 0, 'errmsg': '不在购物车中'})
    except Cart.MultipleObjectsReturned:
        # 购物车表中出现多次
        raise Exception('购物车中同一商品出现多次')
    else:
        # 之前存在,数量+1
        now.delete()
    return JsonResponse({'res': 1})


# 购物车书数量设置为
def set_number(request):
    try:
        book_id = int(request.GET.get('book_id'))
        number = int(request.GET.get('number'))
    except ValueError:
        return JsonResponse({'res': 0, 'errmsg': '参数错误'})

    if number is None:
        raise Exception('未设置set_number数量')

    if number < 0:
        raise Exception('书籍数量不为负')

    if number == 0:
        return cancel(request)

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
            number=number,
            price=book.price,
            select=True,
        )
    except Cart.MultipleObjectsReturned:
        # 购物车表中出现多次
        raise Exception('购物车中同一商品出现多次')
    else:
        # 之前存在,数量=number
        Cart.objects.filter(user_id=request.session['user']['user_id'], book_id=book_id).update(number=number)
    return JsonResponse({'res': 1})


# 购物车书选中状态反转
def select(request):
    try:
        book_id = int(request.GET.get('book_id'))
    except ValueError:
        return JsonResponse({'res': 0, 'error_message': '书籍号错误'})

    try:
        now = Cart.objects.get(user_id=request.session['user']['user_id'], book_id=book_id)
    except Cart.DoesNotExist:
        raise Exception('购物车中商品不存在')
    except Cart.MultipleObjectsReturned:
        raise Exception('购物车中同一商品出现多次')
    else:
        # 之前存在,状态反转
        Cart.objects.filter(user_id=request.session['user']['user_id'], book_id=book_id).update(select=not now.select)
    return JsonResponse({'res': 1})


def count(request):
    if request.session.get('islogin', False):
        cart_list = Cart.objects.filter(user_id=request.session['user']['user_id'])
        return JsonResponse({'res': len(cart_list)})
    else:
        return JsonResponse({'res': -1})