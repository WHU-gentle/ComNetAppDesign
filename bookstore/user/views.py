from django.shortcuts import render
from django.http import Http404

from .models import User


# Create your views here.


def login(request):
    return render(request, 'user/login.html')


def detail(request):
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
        return render(request, 'user/detail.html', {'user': user})


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
