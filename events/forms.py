from django import forms

class ContactForm(forms.Form):
    name = forms.CharField(label='Вашето име (*)', max_length=120)
    email = forms.EmailField(label='Email (*)')
    subject = forms.CharField(label='Тема', max_length=150, required=False)
    message = forms.CharField(label='Вашата порака', widget=forms.Textarea(attrs={'rows':6}))
