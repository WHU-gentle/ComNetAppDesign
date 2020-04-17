import io

from django.forms import model_to_dict
from django.http import JsonResponse, Http404, HttpResponseRedirect, HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse

# Create your views here.
from book.models import Book
from user.models import Cart
from order.models import Order, OrderContent
from django.core import serializers
from bookstore import settings

import datetime

from alipay import AliPay  # https://blog.csdn.net/appleyuchi/article/details/104613313
import qrcode, time
import urllib


def all(request):
    user_id = request.session['user']['user_id']

    # 更新待支付订单状态
    for order in Order.objects.filter(user_id=user_id, status=1):
        # ？频繁连续查询失败概率明显提高？同一顾客不太可能有过多待支付订单
        order_status_update(order)
    def Add_Content(order):
        dic = {0: '已取消', 1: '待付款', 2: '待发货', 3: '已发货', 4: '已完成'}
        order = model_to_dict(order)
        order['status'] = dic[order['status']]
        order_content_list = OrderContent.objects.filter(order_id=order['order_id'])
        order_content = []
        for o_c in order_content_list:
            o_c = model_to_dict(o_c)
            o_c['books'] = Book.objects.get(book_id=o_c['book_id'])
            o_c['price'] = o_c['price'] * o_c['number']
            order_content.append(o_c)
        order['order_content'] = order_content
        return order
    cancel_list = [Add_Content(order) for order in Order.objects.filter(user_id=user_id, status=0)]
    unpaid_list = [Add_Content(order) for order in Order.objects.filter(user_id=user_id, status=1)]
    unsent_list = [Add_Content(order) for order in Order.objects.filter(user_id=user_id, status=2)]
    unreceived_list = [Add_Content(order) for order in Order.objects.filter(user_id=user_id, status=3)]
    finished_list = [Add_Content(order) for order in Order.objects.filter(user_id=user_id, status=4)]
    content = {
        'cancel_list': cancel_list,
        'unpaid_list': unpaid_list,
        'unsent_list': unsent_list,
        'unreceived_list': unreceived_list,
        'finished_list': finished_list,
    }
    # 因为没有对应前端，先返回成json
    return render(request, 'order/all.html', content)


def detail(request, order_id: int):
    content = {}
    # 订单本身的信息
    try:
        order = Order.objects.get(order_id=order_id)
    except Cart.DoesNotExist:
        return Http404
    except Cart.MultipleObjectsReturned:
        raise Exception('同一订单号出现多次')

    # 更新待支付订单状态
    order_status_update(order)

    # object 转 dict
    content['order'] = model_to_dict(order)
    # 计算总付款数=总价+运费
    content['order']['all_price'] = content['order']['sum_price'] + 10

    # 订单中书籍的信息
    content['order_content'] = []
    order_content = OrderContent.objects.filter(order_id=order_id)
    content['count'] = len(order_content)
    for book in order_content:
        element = {
            'id': book.order_id,
            'book_id': book.book_id,
            'number': book.number,
            'price': book.price * book.number,  # 小计：可能不只一本同种书的总价
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
            'book_price': book.price,
            'author': book.author,
            'press': book.press,
            'kind_name': book.kind_name,
        })
        content['order_content'].append(element)
        #收货地址
        content['address'] = request.session['user']['address']
        content['user_name'] = request.session['user']['user_name']
        content['phone_number'] = request.session['user']['phone_number']
    return render(request, 'order/detail.html', content)


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

    # print(order.order_id)

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
    # 重定向展示实际的网址
    print(order.order_id)
    return redirect("/order/detail/%d" % order.order_id)

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
    return JsonResponse({'res':1, 'order_id':order.order_id})

def receive(request):
    try:
        order_id = int(request.GET.get('order_id'))
    except ValueError:
        return JsonResponse({'res': 0, 'errmsg': '订单号错误'})
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


alipayClient = AliPay(
    appid=settings.APP_ID,
    app_notify_url=None,
    app_private_key_string=settings.APP_PRIVATE_KEY,
    alipay_public_key_string=settings.ALIPAY_PUBLIC_KEY,
    sign_type='RSA2',
    debug=settings.DEBUG,
)


def alipay_pay(request):
    global alipayClient

    out_trade_no = request.GET.get('order_id')
    if out_trade_no is None:
        print('无order_id')
        return
    try:
        order_id = int(out_trade_no)
    except ValueError:
        print('order_id非整数')
        return

    if settings.DEBUG:
        # 调试时因为支付宝服务器记录已被扫码的订单状态，每次模拟一个新订单进行调试
        out_trade_no += ('__%s' % datetime.datetime.now()).split('.')[0].replace(' ', '_').replace('-', '_').replace(':', '_')
        print(out_trade_no)

    try:
        order = Order.objects.get(order_id=order_id)
    except Order.DoesNotExist:
        # 订单不存在
        print('order_id 订单不存在')
        return
    except Order.MultipleObjectsReturned:
        raise Exception('订单表错误')

    # 书籍总价加运费
    total_amount = order.sum_price + 10.00
    subject = '珞珈在线书店订单 %s' % order.time_submit
    timeout_express = '30m'
    try:
        dict = alipayClient.api_alipay_trade_precreate(out_trade_no=out_trade_no, total_amount=total_amount,
                                                       subject=subject, timeout_express=timeout_express)
    except urllib.error.URLError:
        raise Exception('网络已断开')

    # https://www.cnblogs.com/linjiqin/p/4140455.html
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=2,  # 图片尽可能小，但足以识别（结果一般为86*86像素）
        border=1
    )
    qr.add_data(dict['qr_code'])  # 从URL获取二维码所含信息
    img = qr.make_image()  # 生成二维码图片
    buf = io.BytesIO()
    # 将图片保存在内存中，文件类型为png
    img.save(buf, 'png')
    # 将内存中的图片数据返回给客户端，MIME类型为图片png
    return HttpResponse(buf.getvalue(), 'image/png')


# 未处理未扫码但长时间未支付的情况
def alipay_query(out_trade_no: str):
    global alipayClient
    try:
        result = alipayClient.api_alipay_trade_query(out_trade_no=out_trade_no)
    except:
        return {'res': 0}

    try:
        if settings.DEBUG:
            order_id = int(out_trade_no.split('_')[0])
        else:
            order_id = int(out_trade_no)
    except ValueError:
        raise Exception('order_id非整数 %s' % out_trade_no)

    if result.get('code', '') == '40004':
        if result.get('sub_code', '') == 'ACQ.TRADE_NOT_EXIST':
            # 用户未扫码，支付宝订单未创建
            return {'res': 1, 'status': 1}
        else:
            # 调用失败
            return {'res': 0}
    elif result.get('code', '') == '10000':
        try:
            order = Order.objects.get(order_id=order_id)
        except Order.DoesNotExist:
            # 订单不存在
            raise Exception('order_id 订单不存在 %d' % order_id)
        except Order.MultipleObjectsReturned:
            raise Exception('订单表错误 %d' % order_id)

        # 待支付状态的订单才会被查询，若未支付无需更新
        if result.get("trade_status", "") == "WAIT_BUYER_PAY":
            # 用户扫码，未支付
            return {'res': 1, 'status': 1}
        elif result.get("trade_status", "") == "TRADE_SUCCESS":
            # 用户已支付
            order.status = 2
            order.time_pay = datetime.datetime.now()
            order.save()
            return {'res': 1, 'status': 2}
        elif result.get("trade_status", "") == "TRADE_CLOSED":
            # 用户超时未支付
            order.status = 0
            order.time_finish = datetime.datetime.now()
            order.save()
            return {'res': 1, 'status': 0}


# 订单状态更新
def order_status_update(order: Order):
    # 待付款订单可能已经付款
    if order.status == 1:
        # 订单提交30分钟未支付即自动取消
        if datetime.datetime.now() - order.time_submit > datetime.timedelta(minutes=30):
            order.status = 0
            order.save()
            return
        # 网络不稳定时最多查询5次，总间隔2秒
        tot = 5
        while True:
            result = alipay_query(str(order.order_id))
            if result['res'] == 1:
                order.status = result['status']
                order.save()
                return
            tot -= 1
            if tot == 0:
                raise Exception('订单状态查询错误')
            print('retry %d' % (5-tot))
            time.sleep((5 - tot) * 0.2)
