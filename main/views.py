from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.conf import settings
from django.contrib.auth import get_user_model
from .models import Article, Assignment, Message, Review
import uuid
import os

# Kullanıcı modelini doğru şekilde al
User = get_user_model()
# Makale yükleme sayfası
def makale_yukle(request):
    if request.method == 'POST':
        email = request.POST.get('email')  # Kullanıcının e-posta adresini al
        title = request.POST.get('title')  # Kullanıcının makale başlığını al

        if not email:
            messages.error(request, "Lütfen geçerli bir e-posta adresi girin.")
            return redirect('makale_yukle')

        if not title:
            messages.error(request, "Lütfen makale başlığını girin.")
            return redirect('makale_yukle')

        # Kullanıcıyı e-posta adresiyle bul veya oluştur
        user, created = User.objects.get_or_create(email=email, defaults={'username': email, 'user_type': 'Yazar', 'is_active': True})

        # Eğer kullanıcı türü Yazar değilse, hata mesajı ver
        if user.user_type != 'Yazar':
            messages.error(request, "Sadece Yazarlar makale yükleyebilir.")
            return redirect('makale_yukle')

        # Yüklenen dosyayı al
        makale = request.FILES.get('makale')

        if makale:
            # Yalnızca PDF dosyalarını kabul et
            if makale.name.endswith('.pdf'):
                tracking_number = str(uuid.uuid4())[:10]  # Takip numarası oluştur

                # Makale oluştur
                Article.objects.create(
                    title=title,  # Kullanıcı tarafından girilen başlık
                    author=user,
                    file=makale,
                    tracking_number=tracking_number
                )

                messages.success(request, f"Makale başarıyla yüklendi! Takip Numaranız: {tracking_number}")
                return redirect('yazar_sayfasi')  # Yazar sayfasına yönlendir

            else:
                messages.error(request, "Yalnızca PDF formatında makale yüklenebilir!")
        else:
            messages.warning(request, "Lütfen bir makale dosyası seçin.")

    return render(request, 'makalesistemi.html')

# Yazar sayfası
def yazar_sayfasi(request):
    articles = None
    email = request.session.get('email', None)  # Oturumdan e-posta al

    if email:
        try:
            user = User.objects.get(email=email)
            articles = Article.objects.filter(author=user).order_by('-submission_date')  # Yazarın makalelerini al
        except User.DoesNotExist:
            messages.error(request, "Böyle bir yazar sistemde kayıtlı değil!")

    return render(request, 'makalesistemi.html', {'email': email, 'articles': articles})

from django.shortcuts import render, get_object_or_404
from django.contrib import messages
from .models import Article

from django.shortcuts import render
from django.contrib import messages
from .models import Article

from django.shortcuts import render
from .models import Article  # Article modelinizin import edildiğinden emin olun
from django.contrib import messages

from django.shortcuts import render
from .models import Article  # Makale modelini içe aktarıyoruz
from django.contrib import messages


def makale_durum_sorgulama(request):
    article = None
    articles = None
    author_articles = None  # Yazarın diğer makaleleri

    if request.method == "POST":
        tracking_number = request.POST.get("tracking_number", "").strip()
        email = request.POST.get("email", "").strip()

        if tracking_number:  # Eğer sadece takip numarası girildiyse
            try:
                article = Article.objects.get(tracking_number=tracking_number)
                author_articles = Article.objects.filter(author=article.author).exclude(tracking_number=tracking_number)
            except Article.DoesNotExist:
                messages.error(request, "Bu takip numarasına ait makale bulunamadı.")

        elif email:  # Eğer sadece e-posta girildiyse
            articles = Article.objects.filter(author__email=email)
            if not articles:
                messages.error(request, "Bu e-posta adresine ait makale bulunamadı.")

    return render(request, "makaledurumsorgulama.html", {
        "article": article,
        "articles": articles,
        "author_articles": author_articles,
    })


# Editör sayfası
def editor_page(request):
    # Tüm makaleleri veritabanından çek
    articles = Article.objects.all()
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

    return render(request, 'editor.html', {'articles': articles})

# Hakem sayfası
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

# Makale değerlendirme sayfası
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

# Makale silme
def delete_article(request, article_id):
    try:
        article = get_object_or_404(Article, id=article_id)
        article.delete()
        return JsonResponse({"success": True})  # ✅ Silme başarılı
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)})  # ❌ Hata varsa bildir

# Mesaj gönderme
def send_message(request):
    if request.method == 'POST':
        # Kullanıcıdan gelen e-posta adresini alıyoruz
        email = request.POST.get('email')
        message_text = request.POST.get('message_text')

        if email and message_text:
            # E-posta adresi ile kullanıcıyı arıyoruz
            user = User.objects.filter(email=email).first()

            # Eğer kullanıcı bulunmazsa, yeni bir kullanıcı oluşturuyoruz
            if not user:
                user = User.objects.create_user(username=email, email=email)  # Kullanıcıyı kaydediyoruz

            # Mesajı veritabanına kaydediyoruz
            message = Message(sender=user, receiver=User.objects.get(user_type='Editor'), message_text=message_text)
            message.save()

            # Başarı mesajını ekliyoruz
            messages.success(request, 'Mesajınız başarıyla gönderildi!')

            # Aynı sayfada kalıp başarı mesajını gösteriyoruz
            return redirect('yazar_sayfasi')  # makalesistemi.html sayfası için url adı buraya yazılmalı

    return render(request, 'send_message.html')

# Tüm makaleleri silme
def delete_all_articles(request):
    if request.method == "POST":
        # Veritabanındaki tüm makaleleri al
        articles = Article.objects.all()

        for article in articles:
            # Dosya yolunu bul
            article_file_path = os.path.join(settings.MEDIA_ROOT, 'articles', article.file.name)

            # Dosyanın var olup olmadığını kontrol et ve sil
            if os.path.exists(article_file_path):
                try:
                    os.remove(article_file_path)
                    messages.success(request, f"{article_file_path} başarıyla silindi.")
                except Exception as e:
                    messages.error(request, f"Dosya silinirken hata oluştu: {str(e)}")
                    continue
            else:
                messages.warning(request, f"Dosya bulunamadı: {article_file_path}")

            # Makaleyi veritabanından sil
            article.delete()

        messages.success(request, "Tüm makaleler ve dosyalar başarıyla silindi.")
        return redirect('editor_page')  # Editör sayfasına yönlendir
    return render(request, 'editor_page.html')

# Makale Revize Etme Sayfası
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import Article

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import Article

def revize_et(request, article_id):
    # Makale mevcut
    article = get_object_or_404(Article, id=article_id)

    if request.method == 'POST':
        # Yüklenen dosya var mı?
        updated_file = request.FILES.get('updated_file')

        if updated_file:
            # Yalnızca PDF dosyasını kabul et
            if updated_file.name.endswith('.pdf'):
                # Makale dosyasını güncelle
                article.file = updated_file
                article.status = 'Revize Edilmiş'  # Makale statüsünü revize edilmiş olarak güncelle

                article.save()
                messages.success(request, "Makale başarıyla revize edilmiştir.")
                return redirect('makale_durum_sorgulama')  # Makale sorgulama sayfasına yönlendir

            else:
                messages.error(request, "Sadece PDF formatındaki dosyalar kabul edilir.")
        else:
            messages.warning(request, "Lütfen revize edilmiş bir dosya yükleyin.")

    return render(request, 'revize_et.html', {'article': article})
