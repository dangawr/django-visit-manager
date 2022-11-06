from django.db import models
from phonenumber_field.modelfields import PhoneNumberField

# Create your models here.


class Client(models.Model):
    first_name = models.CharField(max_length=20)
    second_name = models.CharField(max_length=20)
    phone_number = PhoneNumberField(unique=True)


class Visit(models.Model):
    date = models.DateTimeField()
    client = models.ForeignKey(Client, on_delete=models.deletion.CASCADE, related_name='visits')
    notes = models.TextField(max_length=200)
