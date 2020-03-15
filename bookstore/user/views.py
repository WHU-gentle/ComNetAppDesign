
from django.shortcuts import render, redirect, reverse
from django.http import Http404

from .models import User


# Create your views here.


def login(request):
    return render(request, 'user/login.html')


def detail(request):
    if not request.session.get('islogin', False):
        if request.method == 'POST':
            try:
                user = User.objects.get(pk=request.POST['user_name'])
            except User.DoesNotExist:
                return render(request, 'user/detail.html', {'error_message': '用户不存在'})
            else:
                # print(user.password)
                # print(request.POST['password'])
                if user.password != request.POST['password']:
                    return render(request, 'user/detail.html', {'error_message': '密码错误'})
            request.session['islogin'] = True
            request.session['user'] = {
                'user_name': user.user_name,
                'phone_number': user.phone_number,
                'address': user.address,
            }
        else:
            return render(request, 'user/detail.html', {'error_message': '未登录'})
    context = {
        'user': {
            'user_name': request.session['user']['user_name'],
            'phone_number': request.session['user']['phone_number'],
            'address': request.session['user']['address'],
        }
    }

    return render(request, 'user/detail.html', context)


def cache_clean():
    pass


def logout(request):
    request.session.flush()
    cache_clean()
    # 跳转到首页
    return redirect(reverse('index'))


def register(request):
    return render(request, 'user/register.html')


def result(request):
    if request.method == 'POST':
        if request.POST['password'] != request.POST['repeat_password']:
            return render(request, 'user/result.html', {'error_message': '两次输入密码不一致！'})
        user = User(user_name=request.POST['user_name'], password=request.POST['password'],
                    phone_number=request.POST['phone_number'], address=request.POST['address'], )
        user.save()
        return render(request, 'user/result.html', {'message': '注册成功！', 'user_name': request.POST['user_name']})


def cart(request):
    return render(request, 'user/cart.html')


def order(request):
    return render(request, 'user/order.html')