from django.contrib import admin

# Register your models here.
from .models import User
from .models import Cart


class UserAdmin(admin.ModelAdmin):
    fields = [
        # 'user_id',
        'user_name',
        'password',
        'phone_number',  # +86 0311 86012345
        'address',
        'email',
        'register_date',
    ]


admin.site.register(User, UserAdmin)


class CartAdmin(admin.ModelAdmin):
    fields = [
        'user_id',
        'book_id',
        'number',
        'price',
        'select'
    ]


admin.site.register(Cart, CartAdmin)
