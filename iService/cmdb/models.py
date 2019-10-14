from django.db import models

# Create your models here.
class result(models.Model):
    number = models.CharField(max_length=50)
    name = models.CharField(max_length=45)
    GHO = models.CharField(max_length=10)