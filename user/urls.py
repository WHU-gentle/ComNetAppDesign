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
    # path('order/', views.order, name="order"), TODO 订单确认
    path('verifycode/', views.verifycode, name="verifycode"),
    path('verifyemail/', views.verifyemail, name="verifyemail"),
    path('login_check/', views.login_check, name="login_check"),
    path('register_update/', views.register_update, name="register_update"),

   # path('count/', views.cart_count, name='count'), # TODO 获取用户购物车中商品的数量 base.html
]


