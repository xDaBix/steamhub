from django import forms
from django.core.exceptions import ValidationError
from .models import players  

from datetime import date,timedelta

class Registration(forms.Form):
    firstname = forms.CharField(max_length=50, label='First Name')
    lastname = forms.CharField(max_length=50, label='Last Name')
    contactno = forms.CharField(max_length=10, label='Contact Number')
    email = forms.EmailField(max_length=100, label='Email')
    username = forms.CharField(max_length=6, label='Username')
    password = forms.CharField(
        max_length=50, 
        label='Password',
        widget=forms.PasswordInput
    )
    gender = forms.ChoiceField(
        choices=[('M', 'Male'), ('F', 'Female'), ('O', 'Others')],
        label='Gender',
        widget=forms.Select(attrs={'class': 'gender-dropdown'})
    )
    max_date = (date.today() - timedelta(days=365*16)).strftime('%Y-%m-%d')
    
    date_of_birth = forms.DateField(
        label='Date of Birth',
        widget=forms.DateInput(attrs={
            'type': 'date',
            'min': '1900-01-01',
            'max': max_date
        })
    )
    
   
    

    