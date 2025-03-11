from django.shortcuts import render
from django.contrib import messages
from .models import User, Article
import uuid

def yazar_sayfasi(request):
    articles = None  # Varsayılan olarak makale listesi boş
    email = None

    if request.method == 'POST':
        email = request.POST.get('email')
        makale = request.FILES.get('makale')

        if makale:
            # Kullanıcıyı bul veya oluştur
            user, created = User.objects.get_or_create(username=email, email=email, defaults={'is_active': True})

            # Makale kaydet
            tracking_number = str(uuid.uuid4())[:10]

            article = Article.objects.create(
                title="Makale Başlığı",
                author=user,
                file=makale,
                tracking_number=tracking_number
            )

            messages.success(request, f"Makale başarıyla yüklendi! Takip Numaranız: {tracking_number}")
            # Sadece yüklenen makaleyi görüntülemek
            articles = Article.objects.filter(author=user).order_by('-submission_date')

        else:
            # Kullanıcı e-postasına göre makale sorgulama
            try:
                user = User.objects.get(email=email)
                articles = Article.objects.filter(author=user).order_by('-submission_date')  # Son yüklenen makale üstte
            except User.DoesNotExist:
                messages.error(request, "Böyle bir yazar sistemde kayıtlı değil!")

    return render(request, 'yazar.html', {'email': email, 'articles': articles})

from django.shortcuts import render

from django.shortcuts import render, redirect
from .models import User
from django.contrib import messages

def editor_page(request):
    # Hakemler zaten var mı kontrol et
    existing_reviewers = User.objects.filter(user_type='Hakem')
    if len(existing_reviewers) < 10:
        # 10 adet hakem oluştur
        for i in range(1, 11):
            if not User.objects.filter(username=f'hakem{i}').exists():
                User.objects.create(username=f'hakem{i}', user_type='Hakem')
        messages.success(request, "Hakemler başarıyla oluşturuldu.")
    return render(request, 'editor.html')

def reviewer_page(request):
    return render(request, 'reviewer.html')



