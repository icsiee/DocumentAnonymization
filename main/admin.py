from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import User  # User modelini içe aktar

# Kullanıcı Modelini Admin Paneline Kaydet
@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'user_type', 'is_active', 'is_staff', 'date_joined')
    search_fields = ('username', 'email')
    list_filter = ('user_type', 'is_staff', 'is_active')

from django.contrib import admin
from .models import Article, User  # Article ve User modellerini içe aktar

# Makale Modelini Admin Paneline Kaydet
@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'status', 'submission_date', 'tracking_number')
    search_fields = ('title', 'author__username', 'tracking_number')  # Makale başlığı, yazarın adı ve takip numarası üzerinden arama yapılabilir.
    list_filter = ('status', 'author__user_type')  # Makale durumu ve yazarın kullanıcı tipi üzerinden filtreleme yapılabilir.

