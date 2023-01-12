from django.db import models
from phonenumber_field.modelfields import PhoneNumberField
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser
from decimal import Decimal


class User(AbstractUser):
    email = models.EmailField(blank=True, null=True)
    sms_remainder = models.BooleanField(default=False)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    sms_price = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('0.10'))
    business_name = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return self.username


class Client(models.Model):
    first_name = models.CharField(max_length=20)
    last_name = models.CharField(max_length=20)
    phone_number = PhoneNumberField(unique=True, blank=True)
    user = models.ForeignKey(get_user_model(), on_delete=models.deletion.CASCADE, related_name='clients')

    def __str__(self):
        return f'{self.first_name} {self.last_name}'


class Visit(models.Model):
    date = models.DateField()
    time = models.TimeField()
    client = models.ForeignKey(Client, on_delete=models.deletion.CASCADE, related_name='visits')
    notes = models.TextField(max_length=200, blank=True)

    def __str__(self):
        return f'{self.time} {self.client}'
