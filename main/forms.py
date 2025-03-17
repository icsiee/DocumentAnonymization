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
from .models import Article


class ArticleForm(forms.ModelForm):
    class Meta:
        model = Article
        fields = ['title', 'file', 'content']  # Hangi alanların formda yer alacağını belirtiyoruz

    content = forms.CharField(
        widget=forms.Textarea(attrs={'cols': 80, 'rows': 20, 'placeholder': 'Makale içeriğini buraya yazınız.'}),
        required=False,
        label="Makale İçeriği"
    )

    file = forms.FileField(
        required=False,  # PDF dosyasını yüklemek isteğe bağlıdır
        label="Makale PDF Dosyası"
    )

    # İsteğe bağlı olarak, daha fazla form alanı eklenebilir.

from django import forms
from .models import EditorMessage

class EditorMessageForm(forms.ModelForm):
    class Meta:
        model = EditorMessage
        fields = ['sender_email', 'content']
