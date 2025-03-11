from django.shortcuts import render, redirect
from django.contrib import messages
from .models import User, Article
import uuid  # Benzersiz takip numarası oluşturmak için

def yazar_sayfasi(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        makale = request.FILES.get('makale')

        if email and makale:
            # Kullanıcı mevcut değilse oluştur
            user, created = User.objects.get_or_create(username=email, email=email, defaults={'is_active': True})

            # Makale için benzersiz takip numarası oluştur
            tracking_number = str(uuid.uuid4())[:10]  # Örneğin: 'a1b2c3d4e5'

            # Makale kaydet
            article = Article.objects.create(
                title="Makale Başlığı",  # Burayı uygun şekilde değiştir
                author=user,
                file=makale,
                tracking_number=tracking_number
            )

            messages.success(request, f"Makale başarıyla yüklendi! Takip Numaranız: {tracking_number}")
            return redirect('yazar_sayfasi')  # Aynı sayfaya yönlendir

    return render(request, 'yazar.html')
