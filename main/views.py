
from .models import *
from django.contrib.auth import get_user_model
from collections import defaultdict
from django.contrib import messages
import fitz  # PyMuPDF
import re
from django.http import Http404
from django.http import FileResponse

from .forms import EditorMessageForm
import random
from django.contrib.auth import get_user_model
from .models import Subtopic, ReviewerSubtopic
from django.shortcuts import render, get_object_or_404, redirect
import os
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

User = get_user_model()


User = get_user_model()


def pdf_to_text(pdf_path, txt_path, tracking_number):
    """
    PDF içeriğini çıkararak bir TXT dosyasına kaydeder. Ayrıca PDF'deki resimleri tanıyıp
    her bir resme benzersiz bir isim verir ve bu isimleri metne ekler.
    """
    doc = fitz.open(pdf_path)
    text_content = ""
    image_counter = 1  # Resim sırası
    image_references = []  # Resim referansları (metne eklenecek)

    for page_number, page in enumerate(doc, 1):  # Sayfa numarasını baştan 1'den başlatarak döngüye al
        # Sayfanın metnini al
        page_text = page.get_text("text")

        # Sayfadaki resimleri tespit et
        images = page.get_images(full=True)
        image_positions = []  # Resimlerin bulunduğu metin pozisyonları

        for img_index, img in enumerate(images, 1):
            xref = img[0]  # Resmin XREF numarası
            base_image = doc.extract_image(xref)
            image_filename = f"{tracking_number}_page{page_number}_img{image_counter}.png"

            # Resim dosyasını kaydet
            image_path = os.path.join(settings.MEDIA_ROOT, 'images', image_filename)
            with open(image_path, "wb") as img_file:
                img_file.write(base_image["image"])

            # Resmin yerini metne ekle
            image_position = f"![Resim {image_counter}]({image_filename})"
            image_positions.append(image_position)

            # Resim numarasını artır
            image_counter += 1

        # Resimleri, metnin ilgili yerlerine yerleştir
        for position in image_positions:
            # Sayfadaki metni her bir resmin yerinde uygun şekilde güncelle
            page_text = page_text.replace("{{resim}}", position, 1)

        # Sayfanın metnini genel metne ekle
        text_content += page_text + "\n"

    # TXT dosyasına yaz
    with open(txt_path, "w", encoding="utf-8") as txt_file:
        txt_file.write(text_content)

    return text_content  # Metni döndürerek modelde saklamaya yardımcı olur


User = get_user_model()

def generate_tracking_number():
    """
    5 basamaklı benzersiz bir takip numarası oluşturur.
    """
    while True:
        tracking_number = str(random.randint(10000, 99999))
        if not Article.objects.filter(tracking_number=tracking_number).exists():
            return tracking_number

def makale_yukle(request):
    """
    Kullanıcının makale yükleme işlemini gerçekleştirir.
    - PDF dosyasını yalnızca yazarlar yükleyebilir.
    - PDF'yi takip numarasıyla articles/ klasörüne kaydeder.
    - PDF içeriğini çıkarıp takip numarasıyla text/ klasörüne kaydeder.
    - Takip numarasını veritabanına kaydeder.
    """
    if request.method == 'POST':
        email = request.POST.get('email')
        title = request.POST.get('title')

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
                tracking_number = generate_tracking_number()  # 5 haneli eşsiz takip numarası oluştur

                # Dosya yollarını belirleme
                pdf_filename = f"{tracking_number}.pdf"
                txt_filename = f"{tracking_number}.txt"

                pdf_path = os.path.join(settings.MEDIA_ROOT, 'articles', pdf_filename)
                txt_path = os.path.join(settings.MEDIA_ROOT, 'text', txt_filename)

                # PDF dosyasını kaydet
                with open(pdf_path, 'wb') as destination:
                    for chunk in makale.chunks():
                        destination.write(chunk)

                # PDF içeriğini çıkar ve resimleri kaydet
                extracted_text = pdf_to_text(pdf_path, txt_path, tracking_number)

                # Makaleyi veritabanına kaydet
                Article.objects.create(
                    title=title,
                    author=user,
                    file=f"articles/{pdf_filename}",
                    tracking_number=tracking_number,
                    content=extracted_text
                )

                messages.success(request, f"Makale başarıyla yüklendi! Takip Numaranız: {tracking_number}")
                return redirect('yazar_sayfasi')

            else:
                messages.error(request, "Yalnızca PDF formatında makale yükleyebilirsiniz!")
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


def editor_page(request):
    # Tüm makaleleri veritabanından çek
    articles = Article.objects.all()

    # Hakemler zaten var mı kontrol et
    existing_reviewers = User.objects.filter(user_type='Hakem')

    # Editör bilgisini al
    editor = User.objects.filter(user_type='Editör').first()

    # Editöre gelen mesajları al
    editor_messages = Message.objects.filter(receiver=editor).order_by('-sent_date')

    # Eğer hakem sayısı 10'dan az ise yeni hakemler oluştur
    if existing_reviewers.count() < 10:
        for i in range(1, 11):
            email = f'hakem{i}@gmail.com'  # Hakemlerin e-posta formatı
            if not User.objects.filter(username=email).exists():
                User.objects.create(username=email, user_type='Hakem', email=email)
        assign_reviewers_to_subtopics()

        messages.success(request, "Hakemler başarıyla oluşturuldu.")
    else:
        messages.info(request, "Hakemler zaten oluşturulmuş.")
    reviewers = ReviewerSubtopic.objects.select_related('reviewer', 'subtopic').order_by('reviewer__username')

    grouped_reviewers = defaultdict(list)

    for entry in reviewers:
        grouped_reviewers[entry.reviewer.username].append(entry.subtopic.name)

    # JSON formatına uygun çıktı
    grouped_result = [{"reviewer": reviewer, "subtopics": subtopics} for reviewer, subtopics in
                      grouped_reviewers.items()]

    print(grouped_result)

    hakem=ReviewerSubtopic.objects.all()
    # Şablonu render et
    return render(request, 'editor.html', {
        'editor_messages': editor_messages,
        'articles': articles,
        "reviewers": grouped_result,
    })


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




def extract_text_and_images_from_pdf(pdf_path):
    html_content = ""

    doc = fitz.open(pdf_path)

    for page_num in range(doc.page_count):
        page = doc.load_page(page_num)

        # Sayfa metnini çekiyoruz
        page_text = page.get_text("html")  # HTML formatında metni alıyoruz

        # Sayfa metnindeki sütunları birleştiriyoruz
        page_text = remove_columns(page_text)

        # Sayfadaki görselleri alıyoruz
        for img_index, img in enumerate(page.get_images(full=True)):
            xref = img[0]
            base_image = doc.extract_image(xref)
            image_bytes = base_image["image"]
            image_filename = f"image_{page_num + 1}_{img_index + 1}.png"

            # Görseli kaydediyoruz
            with open(f"media/images/{image_filename}", "wb") as img_file:
                img_file.write(image_bytes)

            # Görselin HTML içindeki yolunu tutuyoruz
            image_url = f"/media/images/{image_filename}"
            page_text += f'<img src="{image_url}" alt="Image {img_index + 1}" />'

        html_content += page_text  # Metni HTML formatında biriktiriyoruz

    return html_content


def remove_columns(html_content):
    """
    PDF'den alınan HTML içeriğindeki sütunları ve karışık yapıları düzeltir.
    """

    # <div> ve <span> gibi öğeleri temizliyoruz ve düzenli bir metin formatına getiriyoruz.
    html_content = re.sub(r'<div[^>]*class="[^"]*column[^"]*"[^>]*>', '', html_content)  # Column div'lerini kaldır
    html_content = re.sub(r'</div>', '', html_content)  # Kapanan div'leri kaldır

    # Eğer <span> gibi öğeler varsa, bunları da temizliyoruz.
    html_content = re.sub(r'<span[^>]*>', '', html_content)
    html_content = re.sub(r'</span>', '', html_content)

    # Boşlukları düzenli hale getiriyoruz
    html_content = re.sub(r'\s+', ' ', html_content)

    # Gereksiz boşlukları, yeni satırları temizliyoruz
    html_content = re.sub(r'\n+', '<br>', html_content)

    return html_content


from django.shortcuts import render
from .models import Article
from django.conf import settings

from django.shortcuts import render
from .models import Article
from django.shortcuts import render
from .models import Article

def revize_et(request, article_id):
    article = Article.objects.get(id=article_id)
    if request.method == "GET":
        # PDF içeriğini çekiyoruz
        html_content = extract_text_and_images_from_pdf(article.file.path)

        # HTML içeriği template'e gönderiyoruz
        return render(request, "revize_et.html", {
            "article": article,
            "pdf_content": html_content,  # HTML içeriği gönderiyoruz
        })


# Yazarın editöre mesaj göndermesi için
def submit_editor_message(request):
    if request.method == "POST":
        form = EditorMessageForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('message_submitted')  # Başarılı gönderim sonrası yönlendirme
    else:
        form = EditorMessageForm()
    return render(request, 'submit_editor_message.html', {'form': form})

# Editörün mesajları görmesi için
def list_editor_messages(request):
    editor_messages = Message.objects.all().filter(receiver_id=request.user.id).order_by('-sent_date')
    print(editor_messages)
    return render(request, 'editor.html', {'editor_messages': editor_messages})


def assign_reviewers_to_subtopics():
    subtopics = list(Subtopic.objects.all())
    reviewers = list(User.objects.filter(user_type='Hakem'))

    if not reviewers:
        return "Hiç hakem bulunamadı!"

    random.shuffle(reviewers)  # Hakemleri karıştır

    assignments = []
    for subtopic in subtopics:
        print(subtopic)
        assigned_reviewer = random.choice(reviewers)  # Rastgele bir hakem seç
        assignment, created = ReviewerSubtopic.objects.get_or_create(
            reviewer=assigned_reviewer,
            subtopic=subtopic
        )
        assignments.append(f"{assigned_reviewer.username} -> {subtopic.name}")

    return assignments  # Atanan hakemleri liste olarak döndür


def revize_et(request, article_id):
    article = get_object_or_404(Article, id=article_id)

    if request.method == "POST":
        # Düzenlenen HTML içeriğini al
        updated_content = request.POST.get("updated_pdf_content", "")

        # Dosya yüklenmiş mi kontrol et
        updated_file = request.FILES.get("updated_file")

        # Eğer yeni bir PDF yüklenmişse, eski dosyayı silip yenisini kaydet
        if updated_file:
            # Eski dosyayı sil (eğer varsa)
            if article.pdf_file:
                old_file_path = os.path.join(settings.MEDIA_ROOT, str(article.pdf_file))
                if os.path.exists(old_file_path):
                    os.remove(old_file_path)

            # Yeni dosyayı kaydet
            article.pdf_file.save(updated_file.name, updated_file)
            article.save()  # Değişiklikleri kaydedin

        # Güncellenen içeriği veritabanına kaydet
        article.content = updated_content
        article.status = "Revize Edildi"  # Durumu güncelle
        article.save()

        return redirect("makale_durum_sorgulama")  # Başarılı işlem sonrası yönlendirme (URL adını değiştir)

    else:
        # PDF içeriğini çıkar ve düzenleme sayfasına gönder
        html_content = extract_text_and_images_from_pdf(article.file.path)
        return render(request, "revize_et.html", {
            "article": article,
            "pdf_content": html_content,
        })






def pdf_goruntule(request, article_id):
    article = get_object_or_404(Article, id=article_id)

    if not article.pdf_file:
        raise Http404("Bu makalenin PDF dosyası mevcut değil.")

    pdf_path = os.path.join(settings.MEDIA_ROOT, 'articles', article.file.name)

    if not os.path.exists(pdf_path):
        raise Http404("PDF dosyası bulunamadı.")

    return FileResponse(open(pdf_path, "rb"), content_type="application/pdf")




@csrf_exempt
def generate_random_reviewers(request):
    if request.method == "POST":
        result = assign_reviewers_to_subtopics()
        return JsonResponse({"message": "Atama işlemi tamamlandı!", "details": result})

    return JsonResponse({"error": "Geçersiz istek"}, status=400)
