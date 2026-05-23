from django import forms
from .models import BuyOrder

class BuyForm(forms.ModelForm):
    class Meta:
        model = BuyOrder
        fields = ["event_title", "email", "first_name", "last_name", "address"]
        widgets = {
            "event_title": forms.TextInput(attrs={"class": "form-control", "placeholder":"Настан (пример: Концерт Х)"}),
            "email": forms.EmailInput(attrs={"class": "form-control", "placeholder":"name@example.com"}),
            "first_name": forms.TextInput(attrs={"class": "form-control"}),
            "last_name": forms.TextInput(attrs={"class": "form-control"}),
            "address": forms.TextInput(attrs={"class": "form-control"}),
        }

class ContactForm(forms.Form):
    name = forms.CharField(max_length=120, widget=forms.TextInput(attrs={"class":"form-control"}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={"class":"form-control"}))
    message = forms.CharField(widget=forms.Textarea(attrs={"class":"form-control", "rows":5}))
