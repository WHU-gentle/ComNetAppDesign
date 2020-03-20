

# ComNetAppDesign

### 计算机网络应用设计实验——网上书店



#### 老师要求

> 应用程序要求实现一个网上书店的基本功能，要求具有前端（用户）和后端（管理）功能，基于Web运行方式。前端具有浏览书目、购物车等功能，后端具有管理书目、基本统计功能。
>
> - 客户端操作系统为Windows



#### 开发环境

- 前端框架：Bootstrap
- 前端开发语言：HTML5   CSS    JavaScript
- 后端框架：Django
- 后端开发语言：Python



#### 数据库

*用户APP*

> | 用户信息表 |               |
> | ---------- | ------------- |
> | 用户号     | user_id       |
> | 用户名     | user_name     |
> | 密码       | password      |
> | 电话       | phone_number  |
> | 地址       | address       |
> | 电子邮件   | email         |
> | 注册日期   | register_date |
>
> 
>
> | 购物车表     |         |
> | ------------ | ------- |
> | 用户号       | user_id |
> | 购物车书籍号 | book_id |
> | 书籍数量     | number  |
> | 书籍单价     | price   |



*书籍APP*

> | 书籍信息表           |              |
> | -------------------- | ------------ |
> | 书籍号               | book_id      |
> | 书名                 | name         |
> | 书籍图片URL          | book_picture |
> | 书籍价格             | price        |
> | 书籍原价             | price_old    |
> | 作者                 | author       |
> | ISBN                 | isbn         |
> | 出版社               | press        |
> | 库存（书本剩余数量） | rest         |
> | 类别号               | kind_id      |
> | 类别名               | kind_name    |
> | 内容简介             | description  |
> | 销量                 | sales        |



*订单APP*

> | 订单表       |             |
> | ------------ | ----------- |
> | 订单号       | order_id    |
> | 用户号       | user_id     |
> | 订单总价     | sum_price   |
> | 订单状态     | status      |
> | 订单提交时间 | time_submit |
> | 订单付款时间 | time_pay    |
> | 订单完成时间 | time_finish |
>
>  
>
> | 订单内容表 |          |
> | ---------- | -------- |
> | 订单号     | order_id |
> | 订单书籍号 | book_id  |
> | 书籍数量   | number   |
> | 书籍单价   | price    |



#### 网页URL

> | 主页       | index/    |
> | ---------- | --------- |
> | 登录       | login/    |
> | 注册       | register/ |
> | 每类书籍   |           |
> | 每本书详情 | detail/   |
> | 购物车     | cart/     |
> | 订单确认页 |           |
> | 我的订单   |           |
> | 我的主页   |           |
> |            |           |
> |            |           |
>
> 