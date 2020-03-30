from django.contrib import admin

# Register your models here.
from .models import Book
class BookAdmin(admin.ModelAdmin):
    list_display = ['book_id', 'book_name', 'book_picture', 'price', 'price_old', 'author',
                    'isbn', 'press', 'rest', 'kind_id', 'kind_name', 'description', 'sales']
    list_filter = ['book_name']
    search_fields = ['book_name']
    list_per_page = 10
    fieldsets = [
        ("base", {"fields": ['book_id', 'book_name', 'press', 'author']}),
        ("describe", {"fields": ['book_picture', 'isbn', 'kind_id', 'kind_name', 'description']}),
        ("sale", {"fields": ['price', 'price_old', 'rest', 'sales']})
    ]
admin.site.register(Book, BookAdmin)