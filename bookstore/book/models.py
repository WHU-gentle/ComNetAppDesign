from django.db import models

# Create your models here.


class Book(models.Model):
    def __str__(self):
        return self.book_name

    book_id = models.AutoField(primary_key=True)
    book_name = models.CharField(max_length=100)
    book_picture = models.CharField(max_length=500)
    price = models.FloatField()
    price_old = models.FloatField()
    author = models.CharField(max_length=50)
    isbn = models.CharField(max_length=20)
    press = models.CharField(max_length=50)
    rest = models.IntegerField()
    kind_id = models.IntegerField()
    kind_name = models.CharField(max_length=20)
    description = models.CharField(max_length=10000)
    sales = models.IntegerField()
