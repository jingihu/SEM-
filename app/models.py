from django.db import models

# Create your models here.
class Speech(models.Model):
    # number = models.IntegerField()
    all_word = models.CharField(max_length=20,null=True)