# orders/forms.py
from django import forms


class CheckoutForm(forms.Form):
    full_name = forms.CharField(label="Полно име", max_length=120)
    phone = forms.CharField(label="Телефонски број", max_length=20)
    email = forms.EmailField(label="Е-маил адреса")
    street = forms.CharField(label="Улица", max_length=200)
    # street_no = forms.CharField(label="Број", max_length=20)
    zip_code = forms.CharField(label="Поштенски код", max_length=10)
    city = forms.CharField(label="Град", max_length=100)


class ContactForm(forms.Form):
    name = forms.CharField(label="Име", max_length=120)
    email = forms.EmailField(label="Е-маил")
    message = forms.CharField(label="Порака", widget=forms.Textarea)
