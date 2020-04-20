from django.shortcuts import render, redirect, reverse
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.forms.models import model_to_dict
from django.core.paginator import Paginator
from django.core.mail import EmailMultiAlternatives
from django.conf import settings

from bookstore.views import login_needful

from .models import Cart
from book.models import Book
from order.models import Order
from user.models import User

import datetime

import time
# 引入绘图模块
from PIL import Image, ImageDraw, ImageFont
# 引入随机函数模块
import random
# 内存文件操作
import io


# Create your views here.


def login(request) -> HttpResponse:
    """显示登录页面"""
    if request.COOKIES.get("user_name"):
        user_name = request.COOKIES.get("user_name")
        checked = 'checked'
    else:
        user_name = ''
        checked = ''
    context = {
        'user_name': user_name,
        'checked': checked,
    }
    return render(request, 'user/login.html', context)


def user_session_login(request, user: User) -> None:
    """将用户信息写入会话"""
    request.session['islogin'] = True
    request.session['user'] = {
        'user_id': user.user_id,
        'user_name': user.user_name,
        'phone_number': user.phone_number,
        'address': user.address,
        'email': user.email,
        'register_date': user.register_date.strftime("%Y-%m-%d"),
    }


def login_check(request) -> JsonResponse:
    """进行用户登录校验"""
    # 1.获取数据
    user_name = request.POST.get('user_name')
    password = request.POST.get('password')
    remember = request.POST.get('remember')
    verifycode = request.POST.get('verifycode')

    # 2.数据校验
    try:
        if not all([user_name, password, remember, verifycode]):
            # 有数据为空
            raise Exception('不能为空')
        if verifycode.upper() != request.session['verifycode'].upper():
            raise Exception('验证码错误')
        # 3.进行处理:根据用户名和密码查找账户信息
        try:
            user = User.objects.get(user_name=request.POST['user_name'])
        except User.DoesNotExist:
            raise Exception('用户不存在')
        else:
            if user.password != request.POST['password']:
                raise Exception('密码错误')
    except Exception as e:
        return JsonResponse({'res': 0, 'errmsg': str(e)})
    finally:
        # 原验证码失效
        request.session['verifycode'] = ''

    next_url = '../../'
    jres = JsonResponse({'res': 1, 'next_url': next_url})

    # 判断是否需要记住用户名
    if remember == 'true':
        # 记住用户名
        jres.set_cookie('user_name', user_name, max_age=7 * 24 * 3600)
    else:
        # 不要记住用户名
        jres.delete_cookie('user_name')

    # 记住用户的登录状态
    user_session_login(request, user)
    return jres


@login_needful
def detail(request) -> HttpResponse:
    """用户信息详情"""
    context = {
        'user_name': request.session['user']['user_name'],
        'phone_number': request.session['user']['phone_number'],
        'address': request.session['user']['address'],
        'email': request.session['user']['email'],
        'register_date': request.session['user']['register_date'],
    }
    return render(request, 'user/detail.html', context)


@login_needful
def logout(request):
    """登出"""
    request.session.flush()
    # 跳转到首页
    return redirect(reverse('index'))


def register(request) -> HttpResponse:
    """注册"""
    return render(request, 'user/register.html')


def register_check(user_name: str, password: str, repeat_password: str, phone_number: str, address: str,
                   email: str, verify_email_address: str, code: str, verify_email_code: str):
    """
    注册信息检测
    :param user_name: 用户名
    :param password: 密码
    :param repeat_password: 重复输入密码
    :param phone_number: 电话号码
    :param address: 地址
    :param email: 电子邮件
    :param verify_email_address: 验证邮件时会话记录的邮箱地址
    :param code: 验证码
    :param verify_email_code: 会话记录的验证码
    :return: 注册信息是否正确
    """
    error_message = []
    error_status = 0
    # 用户名：不为空，不超过16个字符
    if user_name == '':
        error_status |= 1
        error_message.append('用户名为空')
    elif len(user_name) > 16:
        error_status |= 1
        error_message.append('用户名长度超过16个字符')
    # 密码：至少6个字符，不超过16个字符
    if len(password) < 6:
        error_status |= 2
        error_message.append('密码长度不足6个字符')
    elif len(password) > 16:
        error_status |= 2
        error_message.append('密码长度超过16个字符')
    # 重复密码
    if password != repeat_password:
        error_status |= 4
        error_message.append('两次输入的密码不一致')
    # 电话：不为空，不超过20
    if phone_number == '':
        error_status |= 8
        error_message.append('电话号码为空')
    elif len(phone_number) > 20:
        error_status |= 8
        error_message.append('电话号码长度超过20个字符')
    # 地址：不超过100
    if address == '':
        error_status |= 16
        error_message.append('地址为空')
    elif len(address) > 100:
        error_status |= 16
        error_message.append('地址长度超过20个字符')
    # 电子邮箱：不超过50，只含字母数字下划线，以字母开头（似乎不能以下划线开头？）
    #     格式[a-zA-Z][a-zA-Z0-9_]*@([a-zA-Z0-9_\-]+\.)+[a-zA-Z0-9]+
    #     或者只检查有没有@，反正用户收不到邮件自然得改
    if '@' not in email:
        error_status |= 32
        error_message.append('电子邮箱格式不正确')
    elif len(email) > 50:
        error_status |= 32
        error_message.append('电子邮箱长度超过50个字符')
    # 绑定邮箱
    if email != verify_email_address:
        error_status |= 32
        error_message.append('电子邮箱与邮件接收邮箱不一致')
    # 邮件验证码
    if code == '' or code != verify_email_code:
        error_status |= 64
        error_message.append('邮件验证码错误')

    if error_status == 0:
        return {'res': 1}
    else:
        return {'res': 0, 'error_message': error_message, 'error_status': error_status}


def result(request):
    """执行注册，跳转到主页或失败信息页"""
    if request.method != 'POST':
        return render(request, 'user/result.html', {'error_message': '访问方式错误'})
    user_name = request.POST.get('user_name')
    password = request.POST.get('password')
    repeat_password = request.POST.get('repeat_password')
    phone_number = request.POST.get('phone_number')
    address = request.POST.get('address')
    email = request.POST.get('email')
    verify_email_code = request.POST.get('verify_email_code')

    # 检查注册信息
    res = register_check(user_name, password, repeat_password, phone_number, address,
                         email, request.session.get('verify_email_address'),
                         verify_email_code, request.session.get('verify_email_code'))

    if res['res'] == 1:
        user = User(user_name=user_name, password=password,
                    phone_number=phone_number, address=address,
                    email=email, register_date=datetime.datetime.now())
        user.save()
        user_session_login(request, user)
        # 重定向到首页
        return redirect(reverse('index'), permanent=True)
    else:
        return render(request, 'user/result.html',
                      {'error_message': res['error_message'], 'error_status': res['error_status']})


# TODO 更新个人信息
# def register_update(request):
#     if request.method != 'POST':
#         return JsonResponse({'res': 0, 'error_message': '访问方式错误'})
#     user_name = request.POST.get('user_name')
#     old_password = request.POST.get('old_password')
#     password = request.POST.get('password')
#     repeat_password = request.POST.get('repeat_password')
#     phone_number = request.POST.get('phone_number')
#     address = request.POST.get('address')
#     email = request.POST.get('email')
#     verify_email_code = request.POST.get('verify_email_code')
#
#     res = register_check(user_name, password, repeat_password, phone_number, address,
#                          email, request.session.get('verify_email_address'),
#                          verify_email_code, request.session.get('verify_email_code'))
#
#     try:
#         me = User.objects.get(user_id=request.session['user']['user_id'])
#     except User.DoesNotExist:
#         return JsonResponse({'res': 0, 'errmsg': '用户不存在'})
#     except User.MultipleObjectsReturned:
#         raise Exception('用户同一id出现多次')
#     if me.password != old_password:
#         return JsonResponse({'res': 0, 'errmsg': '密码错误'})
#
#     request.session['user'] = {
#         'user_id': request.session['user']['user_id'],
#         'user_name': user_name,
#         'phone_number': phone_number,
#         'address': address,
#         'email': email,
#         'register_date': request.session['user']['register_date'],
#     }
#
#     if res['res'] == 1:
#         User.objects.filter(user_id=request.session['user']['user_id']).update(
#             user_name=user_name,
#             password=password,
#             phone_number=phone_number,
#             address=address,
#             email=email,
#         )
#         return JsonResponse({'res': 1})
#     else:
#         # 有一个报错Expected type 'Iterable[str]', got 'int' instead ??
#         return JsonResponse({'res': 0, 'errmsg': '\n'.join(res['error_message'])})


@login_needful
def cart(request) -> HttpResponse:
    """购物车中的商品信息"""
    u_name = request.session['user']['user_name']
    u_id = User.objects.get(user_name=u_name).user_id
    cart_list = Cart.objects.filter(user_id=u_id)

    # 购物车选中的商品件数：前端计算
    # 购物车所有商品种类数
    total_kinds_count = 0
    cart_data = []
    for cart in cart_list:
        total_kinds_count += 1
        cart = model_to_dict(cart)
        book = Book.objects.get(book_id=cart['book_id'])
        cart['book'] = book
        cart_data.append(cart)
    return render(request, 'user/cart.html', {'cart_list': cart_data, 'total_kinds_count': total_kinds_count})


# def order(request):
#     return render(request, 'user/order.html')


def verifycode(request) -> HttpResponse:
    """会话记录验证码，返回图片"""
    # 设置画面
    # 定义变量，用于画面的背景色、宽、高
    bgcolor = (random.randrange(20, 100), random.randrange(20, 100), 255)
    width = 100
    height = 25
    # 创建画面对象
    im = Image.new('RGB', (width, height), bgcolor)

    # 绘制噪点
    # 创建画笔对象
    draw = ImageDraw.Draw(im)
    # 差异颜色随机绘制噪点
    for i in range(0, 100):
        xy = (random.randrange(0, width), random.randrange(0, height))
        fill = (random.randrange(0, 255), 255, random.randrange(0, 255))
        draw.point(xy, fill=fill)

    # 绘制验证码
    # 定义验证码的备选值
    str1 = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'
    # 随机选取4个值作为验证码
    rand_str = ''
    for i in range(0, 4):
        rand_str += str1[random.randrange(0, len(str1))]
    # 构造字体对象
    font = ImageFont.truetype("courbd.ttf", 15)
    # 构造字体颜色
    fontcolor = (255, random.randrange(0, 255), random.randrange(0, 255))
    # 绘制4个字
    draw.text((5, 2), rand_str[0], font=font, fill=fontcolor)
    draw.text((25, 2), rand_str[1], font=font, fill=fontcolor)
    draw.text((50, 2), rand_str[2], font=font, fill=fontcolor)
    draw.text((75, 2), rand_str[3], font=font, fill=fontcolor)
    # 释放画笔
    del draw

    # 存入session，用于做进一步验证
    request.session['verifycode'] = rand_str
    # 将图片保存在内存中，文件类型为png
    buf = io.BytesIO()
    im.save(buf, 'png')
    # 将内存中的图片数据返回给客户端，MIME类型为图片png
    return HttpResponse(buf.getvalue(), 'image/png')


def verifyemail(request) -> JsonResponse:
    """会话保存验证邮箱地址、验证码，发送验证邮件"""
    email = request.POST.get('email')

    # 生成6位数字，作为验证码
    random.seed(time.time())
    code = '%d%d%d%d%d%d' % (random.randint(0, 9), random.randint(0, 9), random.randint(0, 9),
                             random.randint(0, 9), random.randint(0, 9), random.randint(0, 9))

    # 设置邮件内容
    # 设置发送邮箱、主题、文本内容和html内容
    from_email = settings.DEFAULT_FROM_EMAIL
    subject = '珞珈网上书店 验证码'
    text_content = '验证码:' + code
    html_content = '验证码<br><big><strong>' + code + '</strong></big>'

    try:
        msg = EmailMultiAlternatives(subject, text_content, from_email, [email])
        msg.attach_alternative(html_content, "text/html")
        msg.send()
        # 记录验证码和邮箱地址
        request.session['verify_email_code'] = code
        request.session['verify_email_address'] = email
        return JsonResponse({'res': 1})
    except Exception:
        return JsonResponse({'res': 0, 'errmsg': '邮件发送失败'})


def super_host(request) -> HttpResponse:
    """管理员主页"""
    return render(request, 'user/super/host.html')


def super_book(request, pageid):
    """管理图书页，10本数分一页"""
    allList = Book.objects.all()

    kinds = []
    for book in allList:
        kind = {"kind_id": book.kind_id, "kind_name": book.kind_name}
        if kind not in kinds:
            kinds.append(kind)

    paginator = Paginator(allList, 10)
    if pageid in paginator.page_range:
        page = paginator.page(pageid)
        num = paginator.count
        return render(request, 'user/super/book.html', {"books": page, "num": num, "kinds": kinds})
    else:
        return HttpResponseRedirect("/user/super/book/1/")


def super_bookadd(request) -> HttpResponse:
    """管理员填写新图书信息，只能选择已有类别"""
    allList = Book.objects.all()

    kinds = []
    for book in allList:
        kind = {"kind_id": book.kind_id, "kind_name": book.kind_name}
        if kind not in kinds:
            kinds.append(kind)

    return render(request, 'user/super/bookadd.html', {"kinds": kinds})


def super_bookCreate(request):
    """管理员新增图书，返回执行结果"""
    book_name = request.POST.get("name")
    book_picture = request.POST.get("pictrue")
    price = request.POST.get("price")
    price_old = request.POST.get("price_old")
    author = request.POST.get("author")
    isbn = request.POST.get("isbn")
    press = request.POST.get("press")
    rest = request.POST.get("rest")
    kind_name = request.POST.get("kind_name")
    kind_id = Book.objects.filter(kind_name=kind_name)[0].kind_id
    description = request.POST.get("description")
    sales = 0

    ret = HttpResponseRedirect("/user/super/book/bookadd/")
    try:
        Book.objects.create(
            book_name=book_name,
            book_picture=book_picture,
            price=price,
            price_old=price_old,
            author=author,
            isbn=isbn,
            press=press,
            rest=rest,
            kind_id=kind_id,
            kind_name=kind_name,
            description=description,
            sales=sales
        )
    except:
        ret.set_cookie("bookCreate", 0)

    ret.set_cookie("bookCreate", 1)
    return ret


def super_bookDelete(request, bookid: int) -> HttpResponseRedirect:
    """管理员执行删除图书，返回执行结果"""
    ret = HttpResponseRedirect("/user/super/book/1/")
    ret.set_cookie("bookid", bookid)
    try:
        book = Book.objects.get(book_id=bookid)
    except Book.DoesNotExist:
        ret.set_cookie("bookDelete", 0)
        return ret

    book = Book.objects.get(book_id=bookid).delete()
    ret.set_cookie("bookDelete", 1)
    return ret


def super_bookChange(request, bookid: int):
    """管理员图书信息修改界面"""
    try:
        book = Book.objects.get(book_id=bookid)
    except Book.DoesNotExist:
        return JsonResponse({"msg": "对象不存在", "bookid": bookid})

    return render(request, 'user/super/bookchange.html', {"book": book})


def super_bookUpdate(request, bookid) -> HttpResponseRedirect:
    """管理员修改书籍信息，返回执行结果"""
    ret = HttpResponseRedirect("/user/super/book/change/" + str(bookid) + "/")
    try:
        book = Book.objects.get(book_id=bookid)
    except Book.DoesNotExist:
        ret.set_cookie('bookChange', 0)
        return ret

    book.book_name = request.POST.get("name")
    book.book_picture = request.POST.get("pictrue")
    book.price = request.POST.get("price")
    book.price_old = request.POST.get("price_old")
    book.author = request.POST.get("author")
    book.isbn = request.POST.get("isbn")
    book.press = request.POST.get("press")
    book.rest = request.POST.get("rest")
    book.kind_name = request.POST.get("kind_name")
    book.kind_id = Book.objects.filter(kind_name=book.kind_name)[0].kind_id
    book.description = request.POST.get("description")
    book.save()

    ret.set_cookie('bookChange', 1)
    return ret


def statistic(request) -> HttpResponse:
    """统计各类书籍销售情况"""
    allList = Book.objects.all()

    # 汇总各类别信息
    kinds = []
    for book in allList:
        kind = {
            'kind_id': book.kind_id,
            'kind_name': book.kind_name,
            'kind_sale': 0.0,  # 本类书籍销售额
            'kind_num': 0,  # 本类书籍销售量
            'kind_maxNumBook': None,  # 本类最大销售量书籍
            'kind_minNumBook': None  # 本类最小销售量书籍
        }
        if kind not in kinds:
            kinds.append(kind)

    for book in allList:
        book_kind = book.kind_id;
        for i in range(len(kinds)):
            if kinds[i]['kind_id'] == book_kind:
                kinds[i]['kind_sale'] = kinds[i]['kind_sale'] + book.sales * book.price
                kinds[i]['kind_num'] += book.sales
                if kinds[i]['kind_maxNumBook'] is None:
                    kinds[i]['kind_maxNumBook'] = book
                else:
                    if book.sales > kinds[i]['kind_maxNumBook'].sales:
                        kinds[i]['kind_maxNumBook'] = book
                if kinds[i]['kind_minNumBook'] is None:
                    kinds[i]['kind_minNumBook'] = book
                else:
                    if book.sales < kinds[i]['kind_minNumBook'].sales:
                        kinds[i]['kind_minNumBook'] = book
                break

    # 总体信息
    all_stat = {
        'all_sale': 0,  # 总销售额
        'all_num': 0,  # 总销售量
        'all_maxSaleKind': None,  # 销售额最多的类
        'all_minSaleKind': None  # 销售额最少的类
    }
    for kind in kinds:
        all_stat['all_sale'] += kind['kind_sale']
        all_stat['all_num'] += kind['kind_num']

        if all_stat['all_maxSaleKind'] is None:
            all_stat['all_maxSaleKind'] = kind
        else:
            if kind['kind_sale'] > all_stat['all_maxSaleKind']['kind_sale']:
                all_stat['all_maxSaleKind'] = kind

        if all_stat['all_minSaleKind'] is None:
            all_stat['all_minSaleKind'] = kind
        else:
            if kind['kind_sale'] < all_stat['all_minSaleKind']['kind_sale']:
                all_stat['all_minSaleKind'] = kind

    return render(request, 'user/super/statistic.html', {"books": allList, "kinds": kinds, "all_stat": all_stat})


def super_order(request, pageid: int):
    """查看订单信息"""
    orderList = Order.objects.filter(status=1)
    paginator = Paginator(orderList, 20)
    if pageid in paginator.page_range:
        page = paginator.page(pageid)
        num = paginator.count
        userList = []
        for order in page.object_list:
            user = User.objects.get(user_id=order.user_id)
            userList.append({"username": user.user_name, "address": user.address, "orderid": order.order_id})
        return render(request, 'user/super/order.html', {"orders": page, "num": num, "userList": userList})
    else:
        return HttpResponseRedirect("/user/super/order/1/")


def super_orderSta(request, orderid: int) -> HttpResponseRedirect:
    """订单发货，订单状态值加1"""
    ret = HttpResponseRedirect("/user/super/order/1/")
    ret.set_cookie("orderid", orderid)
    try:
        order = Order.objects.get(order_id=orderid)
    except Book.DoesNotExist:
        ret.set_cookie("orderSta", 0)
        return ret

    order.status += 1
    order.save()
    ret.set_cookie("orderSta", 1)
    return ret
