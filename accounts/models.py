from django.contrib.auth.models import AbstractUser
from django.db import models
from django import forms


class CustomUser(AbstractUser):
    MEMBERSHIP_CHOICES = [
        ('basic', 'Basic'),
        ('premium', 'Premium'),
        ('vip', 'VIP'),
    ]
    first_name = models.CharField(max_length=30)  
    last_name = models.CharField(max_length=30)   
    email = models.EmailField(unique=True)        
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)  


    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name='groups',
        blank=True,
        related_name='custom_user_set',
        related_query_name='user'
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name='user permissions',
        blank=True,
        related_name='custom_user_set',
        related_query_name='user'
    )

    def __str__(self):
        return self.username  

class URL(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    url = models.URLField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)


class Membership(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    level = models.CharField(max_length=10)  
    expiration_date = models.DateField()     

class PaymentForm(forms.Form):
    card_number = forms.CharField(label='Kart Numarası', max_length=16)
    expiration_date = forms.CharField(label='Son Kullanma Tarihi', max_length=5, help_text='MM/YY')
    cvv = forms.CharField(label='CVV', max_length=3)