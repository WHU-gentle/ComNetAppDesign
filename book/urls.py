from django.urls import path

from . import views

# 多个app
app_name = 'book'
urlpatterns = [
    # TODO 书籍详情
    path('detail/<int:book_id>/', views.detail, name='detail'),
    # TODO 书籍分类
    path('kind/<int:kind_id>/', views.kind, name='kind'),
    # TODO 搜索书籍结果
    path('search?<str:keyword>/', views.search, name='search'),
    # 加入购物车指定本书（缺省为1）
    path('buy/', views.buy, name='buy'),
    # 全部移出购物车
    path('cancel/', views.cancel, name='cancel'),
    # 购物车书数目设置为
    path('set_number/', views.set_number, name='set_number'),
    # 购物车书选中状态反转
    path('select/', views.select, name='select'),
]
