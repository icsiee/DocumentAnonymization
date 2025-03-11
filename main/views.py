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

from django.shortcuts import render
from django.contrib import messages
from .models import User


def editor_page(request):
    # Hakemler zaten var mı kontrol et
    existing_reviewers = User.objects.filter(user_type='Hakem')
    if len(existing_reviewers) < 10:
        # 10 adet hakem oluştur
        for i in range(1, 11):
            email = f'hakem{i}@gmail.com'  # Hakemlerin e-posta formatı
            if not User.objects.filter(username=email).exists():
                User.objects.create(username=email, user_type='Hakem', email=email)
        messages.success(request, "Hakemler başarıyla oluşturuldu.")
    else:
        messages.info(request, "Hakemler zaten oluşturulmuş.")

    return render(request, 'editor.html')


def reviewer_page(request):
    return render(request, 'reviewer.html')


# views.py

from django.shortcuts import render, get_object_or_404, redirect
from .models import Article, Review
from django.contrib import messages

from django.shortcuts import render
from django.contrib import messages
from .models import User, Article, Assignment


def reviewer_page(request):
    reviewer_articles = None
    email = None

    if request.method == 'POST':
        email = request.POST.get('email')

        try:
            # Hakem olarak atanan kullanıcıyı bul
            reviewer = User.objects.get(email=email, user_type='Hakem')

            # Editör tarafından atanmış makaleleri al
            assignments = Assignment.objects.filter(reviewer=reviewer)
            reviewer_articles = [assignment.article for assignment in assignments]

            if not reviewer_articles:
                messages.warning(request, "Bu hakem için atanmış makale bulunmamaktadır.")

        except User.DoesNotExist:
            messages.error(request, "Geçersiz bir e-posta adresi girdiniz veya hakem değil!")

    return render(request, 'reviewer.html', {'email': email, 'articles': reviewer_articles})


def review_article(request, article_id):
    article = get_object_or_404(Article, pk=article_id)

    if request.method == 'POST':
        review_text = request.POST.get('review_text')
        comments = request.POST.get('comments')

        # Değerlendirmeyi kaydet
        review = Review.objects.create(
            article=article,
            reviewer=request.user,
            review_text=review_text
        )

        # Başarılı mesaj
        messages.success(request, 'Değerlendirmeniz başarıyla gönderildi.')
        return redirect('reviewer_page')

    return render(request, 'review_article.html', {'selected_article': article})



