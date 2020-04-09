from django.urls import path

from . import views

# 多个app
app_name = 'user'
urlpatterns = [
    # ex: /user/
    path('login/', views.login, name='login'),
    path('detail/', views.detail, name='detail'),
    path('register/', views.register, name="register"),
    path('result/', views.result, name="result"),
    path('logout/', views.logout, name="logout"),
    path('cart/', views.cart, name="cart"),
    path('order/', views.order, name="order"),
    path('verifycode/', views.verifycode, name="verifycode"),
    path('verifyemail/', views.verifyemail, name="verifyemail"),
    path('login_check/', views.login_check, name="login_check"),

    path('add/', views.cart_add, name='add'), # 添加购物车数据
   # path('count/', views.cart_count, name='count'), # 获取用户购物车中商品的数量
]


