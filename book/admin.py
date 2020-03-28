from django.contrib import admin

# Register your models here.
from .models import Book


class BookAdmin(admin.ModelAdmin):
    fields = [
        # 'book_id',
        'book_name',
        'book_picture',
        'price',
        'price_old',
        'author',
        'isbn',
        'press',
        'rest',
        'kind_id',
        'kind_name',
        'description',
        'sales',
    ]


admin.site.register(Book, BookAdmin)
