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
    path('register_update/', views.register_update, name="register_update"),

    #关于统计信息的超级用户的url
    path('super/', views.super_host, name="super_host"),
    path('super/book/<int:pageid>/', views.super_book, name="super_book"),
    path('super/book/create/', views.super_bookCreate, name="super_bookCreate"),
    path('super/book/delete/<int:bookid>/', views.super_bookDelete, name="super_bookDelete"),
    path('super/book/update/<int:bookid>/', views.super_bookUpdate, name="super_bookUpdate"),
    path('super/user/<int:pageid>/', views.super_user, name="super_user"),
    path('super/statistic/', views.statistic, name="statistic"),
]


