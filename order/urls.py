from django.urls import path

from . import views

# 多个app
app_name = 'order'
urlpatterns = [
    # TODO 自己的全部订单
    path('all/', views.all, name='all'),
    # TODO 订单详情
    path('detail/<int:order_id>/', views.detail, name='detail'),
    # 将购物车中的全部货物提交订单
    path('new', views.new, name='new'),
    # 订单确认收货
    path('receive/', views.receive, name='receive'),
]
