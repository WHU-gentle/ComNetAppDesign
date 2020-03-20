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
]
