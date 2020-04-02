from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from .models import Book
# Create your views here.


def detail(request, book_id):
    try:
        book = Book.objects.get(pk=book_id)
    except Book.DoesNotExist:
        return HttpResponse("你所访问的页面不存在", status=404)

    book_detail = {
        'name':book.book_name,
        'picture':book.book_picture,
        'price':book.price,
        'price_old':book.price_old,
        'author':book.author,
        'isbn':book.isbn,
        'press':book.press,
        'rest':book.rest,
        'kind_name':book.kind_name,
        'kind_id':book.kind_id,
        'sales':book.sales,
        'description':book.description,
    }
    return render(request, 'book/detail.html', {'book':book_detail})

def kind(request, kind_id):
    bookList = Book.objects.filter(kind_id=kind_id)
    if len(bookList) == 0:
        return HttpResponse("你所访问的页面不存在", status=404)

    kind_name = bookList[0].kind_name
    books = []
    for book in bookList:
        book_detail = {
            'name':book.book_name,
            'picture': book.book_picture,
            'price': book.price,
            'price_old': book.price_old,
            'author': book.author,
            'press': book.press,
            'rest': book.rest,
            'sales': book.sales,
        }
        books.append(book_detail)
    return render(request, 'book/kind.html', {'books':books, 'kind_name':kind_name})

def sort_by(book):
    return book.sales

def search(request, keyword):
    bookList1 = Book.objects.filter(book_name__contains=keyword)
    bookList2 = Book.objects.filter(author__contains=keyword)
    bookList3 = Book.objects.filter(press__contains=keyword)
    bookList = bookList1.append(bookList2).append(bookList3)
    bookList.sort(key=sort_by, reverse=True)

    books = []
    for book in bookList:
        book_detail = {
            'name': book.book_name,
            'picture': book.book_picture,
            'price': book.price,
            'price_old': book.price_old,
            'author': book.author,
            'press': book.press,
            'rest': book.rest,
            'sales': book.sales,
        }
        books.append(book_detail)
    return JsonResponse({"books":books})

