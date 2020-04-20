from django.shortcuts import render
from user.models import Cart
from django.http import HttpResponse, JsonResponse
from .models import Book
from django.db.models import Q
from bookstore.views import login_needful_json_res_0_errmsg

import datetime
# Create your views here.


def detail(request, book_id: int) -> HttpResponse:
    """书籍详细信息"""
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


def kind(request, kind_id: int) -> HttpResponse:
    """某种类号书籍页面"""
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


def search(request) -> HttpResponse:
    """书籍搜索，在书名、作者和出版社中搜索"""
    keyword = request.POST.get('keyword')
    bookList = Book.objects.filter(
        Q(book_name__contains=keyword) | Q(author__contains=keyword) | Q(press__contains=keyword)) \
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


@login_needful_json_res_0_errmsg
def buy(request) -> JsonResponse:
    """用户将number本书加入购物车（缺省1本）"""
    if request.method == 'POST':
        return JsonResponse({'res': 0, 'errmsg': '访问方式错误'})

    # 数字
    try:
        book_id = int(request.GET.get('book_id'))
        number = int(request.GET.get('number', 1))
    except ValueError:
        # 商品数目不合法
        return JsonResponse({'res': 0, 'errmsg': '商品数量必须为数字'})
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
        Cart.objects.filter(user_id=request.session['user']['user_id'], book_id=book_id) \
            .update(number=now.number + number)
    return JsonResponse({'res': 1, 'msg': '您成功添加了' + str(number) + '本' + str(book.book_name)})


@login_needful_json_res_0_errmsg
def cancel(request) -> JsonResponse:
    """删除用户购物车中商品"""
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
        # 之前存在
        now.delete()
    return JsonResponse({'res': 1})


@login_needful_json_res_0_errmsg
def set_number(request) -> JsonResponse:
    """设置购物车书数量"""
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


@login_needful_json_res_0_errmsg
def select(request):
    """购物车书选中状态反转"""
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


@login_needful_json_res_0_errmsg
def count(request):
    """购物车商品种类数"""
    cart_list = Cart.objects.filter(user_id=request.session['user']['user_id'])
    return JsonResponse({'res': len(cart_list)})


@login_needful_json_res_0_errmsg
def select_count(request):
    """购物车已选中商品总个数"""
    count = 0
    for cart in Cart.objects.filter(user_id=request.session['user']['user_id'], select=True):
        count += cart.number
    return JsonResponse({'res': count})
