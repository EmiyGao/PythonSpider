from django.db import models

# Create your models here.
class result(models.Model):
    id = models.AutoField(primary_key=True)
    Name = models.CharField(max_length=35)
    District = models.CharField(max_length=20)
    Population = models.CharField(max_length=13)
