from django.db import models
from phonenumber_field.modelfields import PhoneNumberField
from django.contrib.auth.models import User


class Client(models.Model):
    first_name = models.CharField(max_length=20)
    last_name = models.CharField(max_length=20)
    phone_number = PhoneNumberField(unique=True)
    user = models.ForeignKey(User, on_delete=models.deletion.CASCADE, related_name='clients')


class Visit(models.Model):
    date = models.DateTimeField()
    client = models.ForeignKey(Client, on_delete=models.deletion.CASCADE, related_name='visits')
    notes = models.TextField(max_length=200)

