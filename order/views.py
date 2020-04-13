from django.forms import model_to_dict
from django.http import JsonResponse, Http404, HttpResponseRedirect, HttpResponse
from django.shortcuts import render, redirect

# Create your views here.
from book.models import Book
from user.models import Cart
from order.models import Order, OrderContent
from django.core import serializers

import datetime

from alipay.aop.api.AlipayClientConfig import AlipayClientConfig  # 客户端配置类
from alipay.aop.api.DefaultAlipayClient import DefaultAlipayClient  # 默认客户端类
from alipay.aop.api.domain.AlipayTradePagePayModel import AlipayTradePagePayModel  # 网站支付数据模型类
from alipay.aop.api.request.AlipayTradePagePayRequest import AlipayTradePagePayRequest  # 网站支付请求类
from django.conf import settings
import random

from alipay.aop.api.util.SignatureUtils import verify_with_rsa

def all(request):
    user_id = request.session['user']['user_id']
    # all_list = [model_to_dict(order) for order in Order.objects.filter(user_id=user_id, status=[s for s in range(0,5)])]
    cancel_list = [model_to_dict(order) for order in Order.objects.filter(user_id=user_id, status=0)]
    unpaid_list = [model_to_dict(order) for order in Order.objects.filter(user_id=user_id, status=1)]
    unsent_list = [model_to_dict(order) for order in Order.objects.filter(user_id=user_id, status=2)]
    unreceived_list = [model_to_dict(order) for order in Order.objects.filter(user_id=user_id, status=3)]
    finished_list = [model_to_dict(order) for order in Order.objects.filter(user_id=user_id, status=4)]
    content = {
        'cancel_list': cancel_list,
        'unpaid_list': unpaid_list,
        'unsent_list': unsent_list,
        'unreceived_list': unreceived_list,
        'finished_list': finished_list,
        # 'all_list': all_list
    }
    # 因为没有对应前端，先返回成json
    return render(request, 'order/all.html', content)


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
    # 计算总付款数=总价+运费
    content['order']['all_price'] = content['order']['sum_price'] + 10

    # 订单中书籍的信息
    content['order_content'] = []
    order_content = OrderContent.objects.filter(order_id=order_id)
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
    # order.save()
    # return JsonResponse({'res': 1, 'order_id':order.order_id})
    return detail(request, order.order_id)


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


def to_pay(request):
    alipay_client_config = AlipayClientConfig()  # 创建配置对象
    alipay_client_config.server_url = settings.ALIPAY_URL  # 网关
    alipay_client_config.app_id = settings.ALIPAY_APPID  # APPID
    alipay_client_config.app_private_key = settings.APP_PRIVATE_KEY  # 应用私钥
    client = DefaultAlipayClient(alipay_client_config=alipay_client_config)  # 使用配置创建客户端
    model = AlipayTradePagePayModel()  # 创建网站支付模型
    model.out_trade_no = str(request.GET['order_id'])  # 商户订单号码
    model.total_amount = float(request.GET['all_price'])  # 支付总额
    # model.subject = request.GET['goods_name']  # 订单标题
    # model.body = '一套完整详细的Python入门视频。'  # 订单描述
    model.product_code = 'FAST_INSTANT_TRADE_PAY'  # 与支付宝签约的产品码名称，目前只支持这一种。
    model.timeout_express = '30m'  # 订单过期关闭时长（分钟）
    pay_request = AlipayTradePagePayRequest(biz_model=model)  # 通过模型创建请求对象
    pay_request.notify_url = settings.ALIPAY_NOTIFY_URL  # 设置回调通知地址（POST）
    pay_request.return_url = settings.ALIPAY_RETURN_URL # 设置回调通知地址（GET）

    response = client.page_execute(pay_request, http_method='GET')  # 获取支付链接
    return HttpResponseRedirect(response)  # 重定向到支付宝支付页面


def check_pay(params):  # 定义检查支付结果的函数
    sign = params.pop('sign', None)  # 取出签名
    params.pop('sign_type')  # 取出签名类型
    params = sorted(params.items(), key=lambda e: e[0], reverse=False)  # 取出字典元素按key的字母升序排序形成列表
    message = "&".join(u"{}={}".format(k, v) for k, v in params).encode()  # 将列表转为二进制参数字符串
    # with open(settings.ALIPAY_PUBLIC_KEY_PATH, 'rb') as public_key: # 打开公钥文件
    try:
        #     status =verify_with_rsa(public_key.read().decode(),message,sign) # 验证签名并获取结果
        status = verify_with_rsa(settings.ALIPAY_PUBLIC_KEY.encode('utf-8').decode('utf-8'), message,
                                 sign)  # 验证签名并获取结果
        return status  # 返回验证结果
    except:  # 如果验证失败，返回假值。
        return False


def pay_result(request):  # 定义处理回调通知的函数
    # 调用成功
    if request.method == 'GET':
        params = request.GET.dict()  # 获取参数字典
        if check_pay(params):  # 调用检查支付结果的函数
            return HttpResponse('调用成功！')
        else:
            return HttpResponse('调用失败！')

    # 支付成功
    if request.method == 'POST':
        params = request.POST.dict()  # 获取参数字典
        if check_pay(params):  # 调用检查支付结果的函数
            '''
                此处编写支付成功后的业务逻辑
            '''
            order_id = int(params['alipay_trade_page_pay_response']['out_trade_no'])
            Order.objects.filter(order_id=order_id).update(
                status=2,
                time_pay=datetime.datetime.now(),
            )
            # print('支付成功！')
            return HttpResponse('success')  # 返回成功信息到支付宝服务器
        else:
            '''
                此处编写支付失败后的业务逻辑
            '''
            return HttpResponse('')
