from django import forms

class MakaleForm(forms.Form):
    email = forms.EmailField()
    makale = forms.FileField()
