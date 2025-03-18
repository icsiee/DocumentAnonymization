from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings  # Import settings to reference the custom user model

# Kullanıcı Modeli (Yazar, Editör, Hakem)
from django.contrib.auth.models import AbstractUser
from django.db import models

SUBTOPICS = [
    ("Derin Öğrenme", "Yapay Zeka ve Makine Öğrenimi"),
    ("Doğal Dil İşleme", "Yapay Zeka ve Makine Öğrenimi"),
    ("Bilgisayarla Görü", "Yapay Zeka ve Makine Öğrenimi"),
    ("Generatif Yapay Zeka", "Yapay Zeka ve Makine Öğrenimi"),
    ("Veri Madenciliği", "Büyük Veri ve Veri Analitiği"),
    ("Veri Görselleştirme", "Büyük Veri ve Veri Analitiği"),
    ("Veri İşleme Sistemleri", "Büyük Veri ve Veri Analitiği"),
    ("Zaman Serisi Analizi", "Büyük Veri ve Veri Analitiği"),
    ("Şifreleme Algoritmaları", "Siber Güvenlik"),
    ("Güvenli Yazılım Geliştirme", "Siber Güvenlik"),
    ("Ağ Güvenliği", "Siber Güvenlik"),
    ("Kimlik Doğrulama Sistemleri", "Siber Güvenlik"),
    ("Adli Bilişim", "Siber Güvenlik"),
]


class User(AbstractUser):
    USER_TYPES = [
        ('Yazar', 'Yazar'),
        ('Editör', 'Editör'),
        ('Hakem', 'Hakem'),
    ]
    user_type = models.CharField(max_length=10, choices=USER_TYPES, default='Yazar')
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='custom_user_groups',  # Varsayılan 'user_set' yerine yeni bir isim veriyoruz
        blank=True
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='custom_user_permissions',  # Varsayılan 'user_set' yerine yeni bir isim veriyoruz
        blank=True
    )


# Makaleler Modeli
from django.contrib.auth.models import User
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Article(models.Model):
    STATUS_CHOICES = [
        ('Gönderildi', 'Gönderildi'),
        ('İncelemede', 'İncelemede'),
        ('Revize Edildi', 'Revize Edildi'),
        ('Tamamlandı', 'Tamamlandı'),
    ]

    id = models.AutoField(primary_key=True)

    title = models.CharField(max_length=255)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, limit_choices_to={'user_type': 'Yazar'})
    file = models.FileField(upload_to='articles/')  # PDF dosyasını yüklemek için alan
    submission_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Gönderildi')
    tracking_number = models.CharField(max_length=50, unique=True)
    content = models.TextField(blank=True, null=True)  # PDF içeriği için yeni alan

    def __str__(self):
        return self.title


# Değerlendirmeler Modeli
class Review(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    reviewer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, limit_choices_to={'user_type': 'Hakem'})
    review_text = models.TextField()
    review_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review for {self.article.title} by {self.reviewer.username}"


# Editör Atamaları Modeli
class Assignment(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    editor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="assigned_articles", limit_choices_to={'user_type': 'Editör'})
    reviewer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="assigned_reviews", limit_choices_to={'user_type': 'Hakem'})
    assignment_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Editor {self.editor.username} assigned {self.article.title} to {self.reviewer.username}"

# Mesajlar Modeli (Yazar ve Editör Arasındaki İletişim)
class Message(models.Model):
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="sent_messages")
    receiver = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="received_messages")
    message_text = models.TextField()
    sent_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message from {self.sender.username} to {self.receiver.username}"

# Makale Versiyonları (Revizyon Takibi İçin)
class ArticleVersion(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name="versions")
    version_number = models.PositiveIntegerField()
    file = models.FileField(upload_to='article_versions/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('article', 'version_number')

    def _str_(self):
        return f"{self.article.title} - Version {self.version_number}"

# Loglama (Kullanıcı İşlemlerini Kaydetmek İçin)
class Log(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    action = models.CharField(max_length=255)
    action_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.action}"


from django.db import models

class EditorMessage(models.Model):
    sender_email = models.EmailField()  # Yazarın e-posta adresi
    content = models.TextField()  # Mesaj içeriği
    sent_at = models.DateTimeField(auto_now_add=True)  # Mesajın gönderildiği zaman

    def __str__(self):
        return f"{self.sender_email} - {self.sent_at}"

class Subtopic(models.Model):
    name = models.CharField(max_length=255, unique=True)
    main_topic = models.CharField(max_length=255)  # Ana başlık: Yapay Zeka, Büyük Veri, Siber Güvenlik gibi

    def __str__(self):
        return self.name


class ReviewerSubtopic(models.Model):
    reviewer = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'user_type': 'Hakem'})
    subtopic = models.ForeignKey(Subtopic, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.reviewer.username} - {self.subtopic.name}"
