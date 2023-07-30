from django.db import models
from django.contrib.auth.models import User


# Create your models here.
class Assignment(models.Model):
    start_date = models.DateField()
    end_date = models.DateField()
    work_load = models.FloatField()
    name = models.CharField(max_length=64)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    # remaining = models.FloatField(default=0)
