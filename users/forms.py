from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Profile

class UserRegisterForm(UserCreationForm):
    email = forms.EmailField()
    name = forms.CharField(max_length=100)
    first_last_name = forms.CharField(max_length=100)
    date_of_birth = forms.DateField(widget=forms.SelectDateWidget(years=range(1900, 2025)))
    country = forms.CharField(max_length=100)
    sex = forms.ChoiceField(choices=[('M', 'Male'), ('F', 'Female')])
    role = forms.ChoiceField(choices=[('Athlete', 'Athlete'), ('Coach', 'Coach')])

    class Meta:
        model = User
        fields = ['username', 'email', 'name', 'first_last_name', 'date_of_birth', 'country', 'sex', 'role', 'password1', 'password2']