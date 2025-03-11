from django import forms

class MakaleForm(forms.Form):
    email = forms.EmailField(label="E-Posta")
    makale = forms.FileField(label="Makale (PDF)", required=True)
