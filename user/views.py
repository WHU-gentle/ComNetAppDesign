from django.shortcuts import render, redirect, reverse
from django.http import Http404, HttpResponse, JsonResponse
from django.forms.models import model_to_dict

from .models import User, Cart
from book.models import Book

import datetime

# Create your views here.
'''
安全性Bug：
每次输错验证码后端强制让原验证码失效（所有前端内容均可能被篡改），前端重新获取
发送验证邮件前也应该输入验证码/设置时间间隔
尽可能缩短验证码有效时间（验证成功/失败后失效，过期失效）
确保验证邮件的地址和最终注册地址相同，避免绑定错误的邮箱
'''


def login(request):
    '''显示登录页面'''
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


def login_check(request):
    '''进行用户登录校验'''
    # 1.获取数据
    user_name = request.POST.get('user_name')
    password = request.POST.get('password')
    remember = request.POST.get('remember')
    verifycode = request.POST.get('verifycode')

    # 2.数据校验
    if not all([user_name, password, remember, verifycode]):
        # 有数据为空
        return JsonResponse({'res': 0, 'errmsg': '不能为空'})

    if verifycode.upper() != request.session['verifycode'].upper():
        return JsonResponse({'res': 0, 'errmsg': '验证码错误'})

    # 3.进行处理:根据用户名和密码查找账户信息
    try:
        user = User.objects.get(user_name=request.POST['user_name'])
    except User.DoesNotExist:
        return JsonResponse({'res': 0, 'errmsg': '用户不存在'})
    else:
        if user.password != request.POST['password']:
            return JsonResponse({'res': 0, 'errmsg': '密码错误'})
    print('ok')
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
    request.session['islogin'] = True
    request.session['user'] = {
        'user_id': user.user_id,
        'user_name': user.user_name,
        'phone_number': user.phone_number,
        'address': user.address,
        'email': user.email,
        'register_date': user.register_date.strftime("%Y-%m-%d %H:%M:%S"),
    }
    cache_clean()
    return jres


def detail(request):
    if request.session.get('islogin', False):
        context = {
            'user': {
                'user_name': request.session['user']['user_name'],
                'phone_number': request.session['user']['phone_number'],
                'address': request.session['user']['address'],
                'email': request.session['user']['email'],
                'register_date': request.session['user']['register_date'],
            }
        }
        return render(request, 'user/detail.html', context)
    else:
        raise Http404


def cache_clean():
    pass


def logout(request):
    request.session.flush()
    cache_clean()
    # 跳转到首页
    return redirect(reverse('index'))


def register(request):
    return render(request, 'user/register.html')


def register_check(user_name, password, repeat_password, phone_number, address, email, verify_code, verifyemail):
    error_message = []
    '''
    用户信息限制：    （中文字符占用空间？）
    '''
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
    # 电话：不为空，不超过20， TODO 只含以下字符0123456789 +-() 如"(+86) 0311 8697-6542"
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
    if '@' in email:
        error_status |= 32
        error_message.append('电子邮箱格式不正确')
    elif len(email) > 50:
        error_status |= 32
        error_message.append('电子邮箱长度超过50个字符')
    # 邮件验证码
    if verify_code == '' or verify_code != verifyemail:
        error_status |= 64
        error_message.append('邮件验证码错误')

    if error_status == 0:
        return {'res': 1}
    else:
        return {'res': 0, 'error_message': error_message, 'error_status': error_status}


def result(request):
    if request.method != 'POST':
        return render(request, 'user/result.html', {'error_message': '访问方式错误'})
    user_name = request.POST.get('user_name')
    password = request.POST.get('password')
    repeat_password = request.POST.get('repeat_password')
    phone_number = request.POST.get('phone_number')
    address = request.POST.get('address')
    email = request.POST.get('email')
    verify_code = request.POST.get('verify_code')

    res = register_check(user_name, password, repeat_password, phone_number, address,
                          email, verify_code, request.session.get('verifyemail'))
    # 无论验证结果，不能再次验证
    request.session['verifycode'] = ''
    if res == 0:
        user = User(user_name=user_name, password=password,
                    phone_number=phone_number, address=address,
                    email=email, register_date=datetime.datetime.now())
        user.save()
        return render(request, 'user/result.html', {'message': '注册成功！', 'user_name': request.POST['user_name']})
    else:
        return render(request, 'user/result.html', {'error_message': res['error_message'], 'error_status': res['error_status']})


def cart(request):
    if request.session.get('islogin', False):
        u_name = request.session['user']['user_name']
        u_id = User.objects.get(user_name=u_name).user_id
        cart_list = Cart.objects.filter(user_id=u_id)
        cart_data = []
        for cart in cart_list:
            cart = model_to_dict(cart)
            book = Book.objects.get(book_id=cart['book_id'])
            cart['book'] = book
            cart_data.append(cart)
        return render(request, 'user/cart.html', {'cart_list': cart_data, 'size': len(cart_data)})
    else:
        return render(request, 'user/login.html')


def order(request):
    return render(request, 'user/order.html')


# 引入绘图模块
from PIL import Image, ImageDraw, ImageFont
# 引入随机函数模块
import random
# 内存文件操作
import io


def verifycode(request):
    # 定义变量，用于画面的背景色、宽、高
    bgcolor = (random.randrange(20, 100), random.randrange(20, 100), 255)
    width = 100
    height = 25
    # 创建画面对象
    im = Image.new('RGB', (width, height), bgcolor)
    # 创建画笔对象
    draw = ImageDraw.Draw(im)
    # 调用画笔的point()函数绘制噪点
    for i in range(0, 100):
        xy = (random.randrange(0, width), random.randrange(0, height))
        fill = (random.randrange(0, 255), 255, random.randrange(0, 255))
        draw.point(xy, fill=fill)
    # 定义验证码的备选值
    # 除去大写I 小写L 字母O 数字0 1
    str1 = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'
    # 随机选取4个值作为验证码
    rand_str = ''
    for i in range(0, 4):
        rand_str += str1[random.randrange(0, len(str1))]
    # 构造字体对象
    # font = ImageFont.truetype(os.path.join(settings.BASE_DIR, "Ubuntu-RI.ttf"), 15)
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
    print(rand_str)

    buf = io.BytesIO()
    # 将图片保存在内存中，文件类型为png
    im.save(buf, 'png')
    # 将内存中的图片数据返回给客户端，MIME类型为图片png
    return HttpResponse(buf.getvalue(), 'image/png')
    # with open('tmp.png', 'wb') as f:
    #     f.write(buf.getvalue())


import smtplib
from email.mime.text import MIMEText
from email.utils import formataddr
import random
import time
import re

from django.conf import settings
from django.core.mail import EmailMultiAlternatives


def verifyemail(request):
    email = request.POST.get('email')
    if not re.match(r'^[a-z0-9][\w\.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):  # TODO 电子邮箱格式
        # 邮箱不合法
        return JsonResponse({'res': 0, 'errmsg': '地址格式错误'})

    # 生成验证码
    random.seed(time.time())
    code = '%d%d%d%d%d%d' % (random.randint(0, 9), random.randint(0, 9), random.randint(0, 9),
                             random.randint(0, 9), random.randint(0, 9), random.randint(0, 9))

    # 邮件内容
    from_email = settings.DEFAULT_FROM_EMAIL
    subject = '珞珈网上书店 验证码'
    text_content = '验证码:' + code
    html_content = '验证码<br><big><strong>' + code + '</strong></big>'

    try:
        msg = EmailMultiAlternatives(subject, text_content, from_email, [email])
        msg.attach_alternative(html_content, "text/html")
        msg.send()
        print("邮件发送成功")
        request.session['verifyemail'] = code
        return JsonResponse({'res': 1})
    except Exception:
        print("邮件发送失败")
        return JsonResponse({'res': 0, 'errmsg': '邮件发送失败'})


#cart模块
def cart_add(request):
    '''向购物车中添加数据'''

    # 接收数据
    book_id = request.POST.get('book_id')
    book_count = request.POST.get('book_count')

    # 进行数据校验
    if not all([book_id, book_count]):
        return JsonResponse({'res':1 , 'errmsg':'数据不完整'})

    book = Book.objects.get_book_by_id(book_id=book_id)
    if book is None:
        # 商品不存在
        return JsonResponse({'res':2, 'errmsg':'商品不存在'})

    try:
        count = int(book_count)
    except Exception as e:
        # 商品数目不合法
        return JsonResponse({'res':3, 'errmsg':'商品数量必须为数字'})

    # 添加商品到购物车

    if book.book_id is None:
        # 如果用户的购车中没有添加过该商品，则添加数据
        cart = Cart(user_id=request.POST['user_id'], book_id=request.POST['book_id'],
                    number=request.POST['number'], price=request.POST['book_price'],
                    select=request.POST['1'])
    else:
        # 如果用户的购车中已经添加过该商品，则累计商品数目
        Cart.number = int(Cart.number) + count
        cart = Cart(user_id=request.POST['user_id'], book_id=request.POST['book_id'],
                    number=request.POST['number'], price=request.POST['book_price'],
                    select=request.POST['1'])
    cart.save()
    # 返回结果
    return JsonResponse({'res': 4})
