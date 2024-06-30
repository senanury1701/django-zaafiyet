from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from .models import URL

CustomUser = get_user_model()

class RegisterForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'first_name', 'last_name', 'password1', 'password2']

def clean_email(self):
    email = self.cleaned_data.get('email')
    if CustomUser.objects.filter(email=email).exists():
        raise ValidationError("Bu e-posta adresi zaten kullanımda.")
    return email

def clean_username(self):
    username = self.cleaned_data.get('username')
    if CustomUser.objects.filter(username=username).exists():
        raise ValidationError("Bu kullanıcı adı zaten kullanımda.")
    return username

class URLForm(forms.ModelForm):
    class Meta:
        model = URL
        fields = ['url']

class PaymentForm(forms.Form):
    card_number = forms.CharField(label='Kart Numarası', max_length=16)
    expiration_date = forms.CharField(label='Son Kullanma Tarihi', max_length=5, help_text='MM/YY')
    cvv = forms.CharField(label='CVV', max_length=3)

class BalanceForm(forms.Form):
    amount = forms.DecimalField(label='Yüklenecek Tutar', max_digits=10, decimal_places=2)