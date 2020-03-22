from django.urls import path

from . import views

# 多个app
app_name = 'order'
urlpatterns = [
    # TODO 自己的全部订单
    path('all/', views.all, name='all'),
    # TODO 订单详情
    path('detail/<int:order_id>/', views.detail, name='detail'),
    # TODO 改变订单状态
    path('change?order_id=<int:order_id>&new_status_id=<int:new_status_id>', views.detail, name='detail'),
    # TODO 将购物车中的全部货物提交订单
    path('new', views.new, name='new'),
]
