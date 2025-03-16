from django import forms

class MakaleForm(forms.Form):
    email = forms.EmailField(label="E-Posta")
    makale = forms.FileField(label="Makale (PDF)", required=True)


from django import forms
from .models import Message, User


from django import forms
from .models import Message
from django.contrib.auth.models import User

class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['receiver', 'message_text']  # Sadece alıcı ve mesaj içeriği

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Alıcıyı (editörü) sınırlıyoruz.
        self.fields['receiver'].queryset = User.objects.filter(user_type='Editör')  # Kullanıcı türüne göre

from django import forms
from .models import EditorMessage

class EditorMessageForm(forms.ModelForm):
    class Meta:
        model = EditorMessage
        fields = ['sender_email', 'content']
