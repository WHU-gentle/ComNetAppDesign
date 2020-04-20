from django.shortcuts import render, redirect, reverse
from django.http import Http404, JsonResponse


# Create your views here.


def index(request):
    return render(request, 'index.html')


def login_needful(func):
    def in_fun(request):
        if request.session.get('islogin', False):
            return func(request)
        else:
            return redirect(reverse('user:login'))
    return in_fun


def login_needful_json_res_0_errmsg(func):
    def in_fun(request):
        if request.session.get('islogin', False):
            return func(request)
        else:
            return JsonResponse({'res': 0, 'errmsg': '未登录'})
    return in_fun
