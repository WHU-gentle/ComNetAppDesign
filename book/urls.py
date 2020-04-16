from django.urls import path

from . import views

# 多个app
app_name = 'book'
urlpatterns = [
    # 书籍详情
    path('detail/<int:book_id>/', views.detail, name='detail'),
    # 书籍分类
    path('kind/<int:kind_id>/', views.kind, name='kind'),
    #搜索书籍结果
    path('search/', views.search, name='search'),
    # 加入购物车指定本书（缺省为1）
    path('buy/', views.buy, name='buy'),
    # 立即购买创建订单不添加购物车表项
    path('buynow/', views.buynow, name='buynow'),
    # 删除用户购物车中商品的信息
    path('cancel/', views.cancel, name='cancel'),
    # 购物车书数目设置为
    path('set_number/', views.set_number, name='set_number'),
    # 购物车书选中状态反转
    path('select/', views.select, name='select'),
    # 获取用户购物车中商品的数量（无论选不选中的商品种类数）
    path('count/', views.count, name='count'),
    # 购物车已选中数量
    path('select_count/', views.select_count, name='select_count'),
    #path('update/', views.cart_update, name="update"),
]
