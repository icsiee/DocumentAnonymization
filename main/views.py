from django.shortcuts import render
from django.contrib import messages
from .models import User, Article
import uuid

from django.shortcuts import render
from django.contrib import messages
from .models import User, Article
import uuid

from django.shortcuts import render
from django.contrib import messages
from .models import User, Article
import uuid

from django.shortcuts import render, redirect
from django.contrib import messages
from .models import User, Article
import uuid

def yazar_sayfasi(request):
    articles = None
    email = request.session.get('email', None)  # Oturumdan e-posta al

    if request.method == 'POST':
        email = request.POST.get('email')
        request.session['email'] = email  # E-postayı oturuma kaydet

        # Yalnızca PDF formatında dosya yüklenebilir
        makale = request.FILES.get('makale')

        if makale and makale.name.endswith('.pdf'):  # Yalnızca PDF kabul et
            user, created = User.objects.get_or_create(username=email, email=email, defaults={'is_active': True})
            tracking_number = str(uuid.uuid4())[:10]

            Article.objects.create(
                title="Makale Başlığı",
                author=user,
                file=makale,
                tracking_number=tracking_number
            )

            messages.success(request, f"Makale başarıyla yüklendi! Takip Numaranız: {tracking_number}")

            # Başarıyla yüklenen makaleyi kaydettikten sonra formu sıfırla ve aynı sayfaya yönlendir
            return redirect('yazar_sayfasi')  # Sayfayı yenileyerek formu sıfırla

        elif makale:
            messages.error(request, "Yalnızca PDF formatında makale yüklenebilir!")
        else:
            messages.warning(request, "Lütfen bir makale dosyası seçin.")

    if email:
        try:
            user = User.objects.get(email=email)
            articles = Article.objects.filter(author=user).order_by('-submission_date')  # Güncellenmiş liste
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

from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from .models import Article  # Makale modelini içe aktar

from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.contrib import messages
from .models import Article

from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from .models import Article

from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from .models import Article
from django.views.decorators.csrf import csrf_exempt

from django.shortcuts import get_object_or_404, redirect
from django.http import JsonResponse
from django.contrib import messages
from .models import Article

from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from .models import Article

def delete_article(request, article_id):
    try:
        article = get_object_or_404(Article, id=article_id)
        article.delete()
        return JsonResponse({"success": True})  # ✅ Silme başarılı
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)})  # ❌ Hata varsa bildir


from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import MessageForm
from .models import Message

from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from .forms import MessageForm
from .models import Message

from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from .forms import MessageForm
from .models import Message

from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from .models import Message

from django.contrib import messages
from django.shortcuts import render, redirect
from main.models import User  # main.User modelini kullanıyoruz
from .models import Message

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
            return redirect('yazar_sayfasi')  # yazar.html sayfası için url adı buraya yazılmalı

    return render(request, 'send_message.html')


