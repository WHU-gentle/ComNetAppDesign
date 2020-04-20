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
    # path('order/', views.order, name="order"), TODO 订单确认页面
    path('verifycode/', views.verifycode, name="verifycode"),
    path('verifyemail/', views.verifyemail, name="verifyemail"),
    path('login_check/', views.login_check, name="login_check"),
    # path('register_update/', views.register_update, name="register_update"), TODO 更新个人信息

    #关于统计信息的超级用户的url
    path('super/', views.super_host, name="super_host"),
    path('super/book/<int:pageid>/', views.super_book, name="super_book"),
    path('super/book/bookadd/', views.super_bookadd, name="super_bookadd"),
    path('super/book/create/', views.super_bookCreate, name="super_bookCreate"),
    path('super/book/delete/<int:bookid>/', views.super_bookDelete, name="super_bookDelete"),
    path('super/book/change/<int:bookid>/', views.super_bookChange, name="super_bookChange"),
    path('super/book/update/<int:bookid>/', views.super_bookUpdate, name="super_bookUpdate"),
    path('super/statistic/', views.statistic, name="statistic"),
    path('super/order/<int:pageid>/', views.super_order, name="super_oder"),
    path('super/order/status/<int:orderid>/', views.super_orderSta),
]


