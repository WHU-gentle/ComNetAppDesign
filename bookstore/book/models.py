from django.db import models

# Create your models here.


class Book(models.Model):
    def __str__(self):
        return self.book_name

    book_id = models.AutoField(primary_key=True)
    book_name = models.CharField(max_length=100)
    price = models.FloatField()
    author = models.CharField(max_length=50)
    isbn = models.CharField(max_length=20)
    press = models.CharField(max_length=50)
    on_sale = models.BooleanField()