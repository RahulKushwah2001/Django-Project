from django import forms
from .models import Organization, CustomUser

class OrganizationForm(forms.ModelForm):
    class Meta:
        model = Organization
        fields = ['name', 'industry', 'address', 'contact_email']

class UserRegistrationForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'mobile', 'organization']
        widgets = {
            'username': forms.TextInput(attrs={'placeholder': 'Enter username'}),
            'email': forms.EmailInput(attrs={'placeholder': 'Enter email'}),
            'mobile': forms.TextInput(attrs={'placeholder': 'Enter mobile number'}),
            'organization': forms.TextInput(attrs={'placeholder': 'Enter organization name'}),
        }