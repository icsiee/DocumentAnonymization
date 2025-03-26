
from .forms import *

from django.views.decorators.csrf import csrf_exempt
from .utils import *

User = get_user_model()

import fitz  # PyMuPDF
import spacy


nlp = spacy.load("en_core_web_sm")

import torch
from transformers import BertTokenizer, BertModel
from sklearn.metrics.pairwise import cosine_similarity

# 🔹 Önceden tanımlanmış konu ve alt konular
import random
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.shortcuts import redirect, render
from .models import Subtopic, ReviewerSubtopic, User  # Modelleri import et

User = get_user_model()  # Kullanıcı modelini al

# Konu haritasını fonksiyon içinde tanımla, hata almayı önler
import random
from django.contrib import messages
from django.shortcuts import render, redirect
from .models import Subtopic, ReviewerSubtopic, User

# Konu haritası
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import User, Subtopic, ReviewerSubtopic
TOPIC_MAP = [
            ("Deep Learning", "Artificial Intelligence and Machine Learning"),
            ("Natural Language Processing", "Artificial Intelligence and Machine Learning"),
            ("Computer Vision", "Artificial Intelligence and Machine Learning"),
            ("Generative Artificial Intelligence", "Artificial Intelligence and Machine Learning"),
            ("Data Mining", "Big Data and Data Analytics"),
            ("Data Visualization", "Big Data and Data Analytics"),
            ("Data Processing Systems", "Big Data and Data Analytics"),
            ("Time Series Analysis", "Big Data and Data Analytics"),
            ("Encryption Algorithms", "Cyber Security"),
            ("Secure Software Development", "Cyber Security"),
            ("Network Security", "Cyber Security"),
            ("Authentication Systems", "Cyber Security"),
            ("Forensic Computing", "Cyber Security"),
        ]
# Hakemler ve Konuların Oluşturulması
import random
from django.contrib import messages
from .models import User, Subtopic, ReviewerSubtopic

def create_reviewers_and_assign_topics(request):
    if request.method == "POST":
        try:
            # 1️⃣ Hakemleri oluştur
            reviewer_users = []
            for i in range(1, 14):  # 13 hakem
                reviewer, created = User.objects.get_or_create(
                    username=f"hakem{i}",
                    defaults={"user_type": "Reviewer", "email": f"hakem{i}@gmail.com"}
                )
                reviewer_users.append(reviewer)
                print(f"Reviewer created: {reviewer.username}")  # Debug print

            # 2️⃣ Konuları oluştur
            subtopics = []
            TOPIC_MAP = [
                ("Deep Learning", "Artificial Intelligence and Machine Learning"),
                ("Natural Language Processing", "Artificial Intelligence and Machine Learning"),
                ("Computer Vision", "Artificial Intelligence and Machine Learning"),
                ("Generative Artificial Intelligence", "Artificial Intelligence and Machine Learning"),
                ("Data Mining", "Big Data and Data Analytics"),
                ("Data Visualization", "Big Data and Data Analytics"),
                ("Data Processing Systems", "Big Data and Data Analytics"),
                ("Time Series Analysis", "Big Data and Data Analytics"),
                ("Encryption Algorithms", "Cyber Security"),
                ("Secure Software Development", "Cyber Security"),
                ("Network Security", "Cyber Security"),
                ("Authentication Systems", "Cyber Security"),
                ("Forensic Computing", "Cyber Security"),
            ]

            for subtopic_name, main_topic in TOPIC_MAP:
                subtopic, created = Subtopic.objects.get_or_create(
                    name=subtopic_name,
                    defaults={"main_topic": main_topic}
                )
                subtopics.append(subtopic)
                print(f"Subtopic created: {subtopic.name}")  # Debug print

            # 3️⃣ Hakemlere rastgele konu ata
            assigned_topics = set()
            for reviewer in reviewer_users:
                num_topics = random.randint(1, 5)  # Her hakeme 1-5 konu atanacak
                assigned_subtopics = random.sample(subtopics, num_topics)

                for subtopic in assigned_subtopics:
                    _, created = ReviewerSubtopic.objects.get_or_create(reviewer=reviewer, subtopic=subtopic)
                    if created:
                        assigned_topics.add(subtopic)
                    print(f"Assigned {subtopic.name} to {reviewer.username}")  # Debug print

            # 4️⃣ Boşta kalan konuları atama
            unassigned_topics = set(subtopics) - assigned_topics
            for subtopic in unassigned_topics:
                random_reviewer = random.choice(reviewer_users)
                ReviewerSubtopic.objects.get_or_create(reviewer=random_reviewer, subtopic=subtopic)
                print(f"Assigned remaining {subtopic.name} to {random_reviewer.username}")  # Debug print

            messages.success(request, "Hakemler ve konular başarıyla oluşturuldu ve atandı!")
        except Exception as e:
            messages.error(request, f"Bir hata oluştu: {e}")
            print(f"Error occurred: {e}")  # Debug print
        return redirect("editor_page")

    return redirect("editor_page")


import random
from django.contrib import messages
from django.shortcuts import render, redirect
from .models import User, Subtopic, ReviewerSubtopic, Article, Message

import random
from django.contrib import messages
from django.shortcuts import render, redirect
from .models import User, Subtopic, ReviewerSubtopic, Article, Message


import random
from django.contrib import messages
from django.shortcuts import render
from .models import User, Article, Message, Subtopic, ReviewerSubtopic

import random
from django.contrib import messages
from django.shortcuts import render
from .models import User, Article, Message, Subtopic, ReviewerSubtopic

import random
from django.contrib import messages
from django.shortcuts import render
from .models import User, Article, Message, Subtopic, ReviewerSubtopic

import random
from django.contrib import messages
from django.shortcuts import render
from .models import User, Article, Message, Subtopic, ReviewerSubtopic

def editor_page(request):
    """Editör sayfası işlemleri"""

    # 1️⃣ Editör, makaleler ve mesajları al
    articles = Article.objects.all()
    editor = User.objects.filter(user_type='Editör').first()
    editor_messages = Message.objects.filter(receiver=editor).order_by('-sent_date')

    # 2️⃣ Hakemleri ve atanan konuları al
    reviewers = User.objects.filter(user_type='Hakem')  # Hakemleri alıyoruz
    reviewer_subtopics = ReviewerSubtopic.objects.select_related('reviewer', 'subtopic').all()

    # 3️⃣ Hakemleri oluştur
    reviewer_users = []
    for i in range(1, 14):  # 13 hakem
        reviewer, created = User.objects.get_or_create(
            username=f"hakem{i}",
            defaults={"user_type": "Hakem", "email": f"hakem{i}@gmail.com"}
        )
        reviewer_users.append(reviewer)

    # 4️⃣ Konuları oluştur
    subtopics = []
    TOPIC_MAP = [
        ("Deep Learning", "Artificial Intelligence and Machine Learning"),
        ("Natural Language Processing", "Artificial Intelligence and Machine Learning"),
        ("Computer Vision", "Artificial Intelligence and Machine Learning"),
        ("Generative Artificial Intelligence", "Artificial Intelligence and Machine Learning"),
        ("Data Mining", "Big Data and Data Analytics"),
        ("Data Visualization", "Big Data and Data Analytics"),
        ("Data Processing Systems", "Big Data and Data Analytics"),
        ("Time Series Analysis", "Big Data and Data Analytics"),
        ("Encryption Algorithms", "Cyber Security"),
        ("Secure Software Development", "Cyber Security"),
        ("Network Security", "Cyber Security"),
        ("Authentication Systems", "Cyber Security"),
        ("Forensic Computing", "Cyber Security"),
    ]

    for subtopic_name, main_topic in TOPIC_MAP:
        subtopic, created = Subtopic.objects.get_or_create(
            name=subtopic_name,
            defaults={"main_topic": main_topic}
        )
        subtopics.append(subtopic)

    # 5️⃣ Her hakeme sırasıyla bir konu ata
    for i, reviewer in enumerate(reviewer_users):
        subtopic = subtopics[i]  # İlk konuyu sırasıyla hakemlere ata
        ReviewerSubtopic.objects.get_or_create(reviewer=reviewer, subtopic=subtopic)

    # 6️⃣ Kalan konuları rastgele dağıt
    all_assigned_subtopics = [subtopics[i] for i in range(13)]  # İlk başta atanmış konular
    remaining_subtopics = [subtopic for subtopic in subtopics if subtopic not in all_assigned_subtopics]  # Kalan konular

    for reviewer in reviewer_users:
        # Kalan konulardan rastgele birini ata
        available_subtopics = [subtopic for subtopic in remaining_subtopics if subtopic not in all_assigned_subtopics]
        if available_subtopics:  # Eğer boşta konu varsa
            subtopic = random.choice(available_subtopics)
            ReviewerSubtopic.objects.get_or_create(reviewer=reviewer, subtopic=subtopic)
            all_assigned_subtopics.append(subtopic)  # Bu konu artık atanmış olarak ekleniyor

    # 7️⃣ Başarılı mesajı gönder
    messages.success(request, "Hakemler ve konular başarıyla oluşturuldu ve atandı!")

    # 8️⃣ Veriyi render et
    return render(request, 'editor.html', {
        'editor_messages': editor_messages,
        'articles': articles,
        'reviewers': reviewers,  # Hakemler burada gönderilecek
        'reviewer_subtopics': reviewer_subtopics  # Hakemlerin atandığı konular burada gönderilecek
    })




# BERT Modeli ve Tokenizer Yükleme
tokenizer = BertTokenizer.from_pretrained("bert-base-uncased")
model = BertModel.from_pretrained("bert-base-uncased")


def get_text_embedding(text):
    """Metni BERT kullanarak vektör haline getirir."""
    inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True, max_length=512)
    with torch.no_grad():
        outputs = model(**inputs)
    return outputs.last_hidden_state.mean(dim=1).numpy()  # Ortalama vektörü al


def determine_article_topic_bert(article):
    """BERT modelini kullanarak makalenin konusunu belirler ve günceller."""
    txt_path = os.path.join(settings.MEDIA_ROOT, "text", f"{article.tracking_number}.txt")

    try:
        with open(txt_path, "r", encoding="utf-8") as file:
            content = file.read()
    except FileNotFoundError:
        print(f"Hata: {txt_path} bulunamadı.")
        return

    # 📌 Makale içeriğinin vektörünü al
    article_embedding = get_text_embedding(content)

    best_match = None
    best_score = -1

    for subtopic, main_topic in TOPIC_MAP:
        subtopic_embedding = get_text_embedding(subtopic)  # Alt başlık için embedding al
        score = cosine_similarity(article_embedding, subtopic_embedding)[0][0]  # Benzerlik hesapla

        if score > best_score:
            best_score = score
            best_match = (main_topic, subtopic)

    if best_match and best_score > 0.5:  # Benzerlik eşiği belirlenebilir
        article.topic, article.subtopic = best_match
    else:
        article.topic, article.subtopic = "Bilinmiyor", "Bilinmiyor"

    article.save(update_fields=["topic", "subtopic"])
    print(f"Eşleşme bulundu: {article.subtopic} -> {article.topic}")


def makale_yukle(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        title = request.POST.get('title')

        if not email:
            messages.error(request, "Lütfen geçerli bir e-posta adresi girin.")
            return redirect('makale_yukle')

        if not title:
            messages.error(request, "Lütfen makale başlığını girin.")
            return redirect('makale_yukle')

        user, created = User.objects.get_or_create(email=email, defaults={'username': email, 'user_type': 'Yazar', 'is_active': True})

        if user.user_type != 'Yazar':
            messages.error(request, "Sadece Yazarlar makale yükleyebilir.")
            return redirect('makale_yukle')

        makale = request.FILES.get('makale')

        if makale and makale.name.endswith('.pdf'):
            tracking_number = generate_tracking_number()

            pdf_filename = f"{tracking_number}.pdf"
            txt_filename = f"{tracking_number}.txt"

            pdf_path = os.path.join(settings.MEDIA_ROOT, 'articles', pdf_filename)
            txt_path = os.path.join(settings.MEDIA_ROOT, 'text', txt_filename)

            with open(pdf_path, 'wb') as destination:
                for chunk in makale.chunks():
                    destination.write(chunk)

            # PDF içeriğini çıkarıp TXT olarak kaydet
            extracted_text = pdf_to_text(pdf_path, txt_path, tracking_number)

            # 🔹 Makaleyi kaydet (başlangıçta bilinmiyor)
            article = Article.objects.create(
                title=title,
                author=user,
                file=f"articles/{pdf_filename}",
                tracking_number=tracking_number,
                content=extracted_text,
                topic="Bilinmiyor",
                subtopic="Bilinmiyor"
            )

            # 🔹 Konu belirleme işlemi burada çalıştırılır
            determine_article_topic_bert(article)

            messages.success(request, f"Makale başarıyla yüklendi! Takip Numaranız: {tracking_number}")
            return redirect('yazar_sayfasi')

        else:
            messages.error(request, "Lütfen yalnızca PDF formatında dosya yükleyin!")

    return render(request, 'makalesistemi.html')


import spacy

# spaCy dil modeli yükleniyor
nlp = spacy.load("en_core_web_sm")


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


import random
from collections import defaultdict
from django.shortcuts import render
from django.http import JsonResponse
from django.contrib import messages
from .models import Article, User, Message, ReviewerSubtopic, MainSubtopic

from collections import defaultdict
import random
from django.shortcuts import render
from django.contrib import messages
from .models import Subtopic





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

import os
import shutil


def delete_all_articles(request):
    if request.method == "POST":
        # 1️⃣ Tüm makaleleri veritabanından al
        articles = Article.objects.all()

        for article in articles:
            # 2️⃣ Makale dosyasını sil
            if article.file:
                article_file_path = os.path.join(settings.MEDIA_ROOT, article.file.name)

                if os.path.exists(article_file_path):
                    try:
                        os.remove(article_file_path)
                        messages.success(request, f"{article_file_path} başarıyla silindi.")
                    except Exception as e:
                        messages.error(request, f"Dosya silinirken hata oluştu: {str(e)}")

            # 3️⃣ Makaleyi veritabanından sil
            article.delete()

        # 4️⃣ Belirtilen klasörleri temizle
        folders_to_clear = ['images', 'articles', 'text']  # Sadece klasör isimleri
        for folder in folders_to_clear:
            folder_path = os.path.join(settings.MEDIA_ROOT, folder)  # Tam yol oluştur

            if os.path.exists(folder_path):  # Klasör varsa işlemi yap
                try:
                    # Tüm içeriği sil, ama klasörü değil
                    for filename in os.listdir(folder_path):
                        file_path = os.path.join(folder_path, filename)
                        if os.path.isfile(file_path) or os.path.islink(file_path):
                            os.unlink(file_path)  # Dosya veya sembolik link sil
                        elif os.path.isdir(file_path):
                            shutil.rmtree(file_path)  # Alt klasörü tamamen sil

                    messages.success(request, f"{folder} klasörü başarıyla temizlendi.")
                except Exception as e:
                    messages.error(request, f"{folder} klasörü temizlenirken hata oluştu: {str(e)}")

        messages.success(request, "Tüm makaleler ve medya dosyaları başarıyla silindi.")
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
    # Makaleyi al
    article = get_object_or_404(Article, id=article_id)

    if request.method == "POST":
        # Düzenlenen HTML içeriğini al
        updated_content = request.POST.get("updated_pdf_content", "").strip()

        # Dosya yüklenmiş mi kontrol et
        updated_file = request.FILES.get("updated_file")

        # Eğer yeni bir PDF dosyası yüklenmişse
        if updated_file:
            # Eski PDF dosyasını sil
            if article.pdf_file:
                old_file_path = os.path.join(settings.MEDIA_ROOT, "articles", str(article.pdf_file))
                if os.path.exists(old_file_path):
                    os.remove(old_file_path)

            # Yeni PDF dosyasını kaydet
            article.pdf_file.save(updated_file.name, updated_file)

        # Makale içeriğini ve durumu güncelle
        article.content = updated_content
        article.status = "Revize Edildi"  # Durum güncelle
        article.save()

        # İçeriği metin dosyasına kaydet (media/text/{tracking_number}.txt)
        txt_path = os.path.join(settings.MEDIA_ROOT, "text", f"{article.tracking_number}.txt")
        with open(txt_path, "w", encoding="utf-8") as file:
            file.write(updated_content)

        # Resimleri media/images klasöründen al
        images = []
        for i in range(1, 100):  # Sayfa ve resim numarasını sınırsız kabul edebiliriz
            img_path = os.path.join(settings.MEDIA_ROOT, "images", f"{article.tracking_number}_page{i}_img1.png")
            if os.path.exists(img_path):
                images.append(img_path)
            else:
                break  # Resim yoksa döngüyü sonlandır

        # Yeni PDF'i oluştur
        new_pdf_path = os.path.join(settings.MEDIA_ROOT, "articles", f"{article.tracking_number}.pdf")
        generate_pdf_with_images_and_text(updated_content, images, new_pdf_path)

        # Yeni PDF'i veritabanına kaydet
        article.file.name = f"articles/{article.tracking_number}.pdf"
        article.save()

        # Kullanıcıya başarı mesajı göster
        messages.success(request, "Makale başarıyla revize edildi!")

        # Başarıyla tamamlandıktan sonra başka bir sayfaya yönlendirin
        return redirect("makale_durum_sorgulama")

    else:
        # Eğer GET isteği ise PDF içeriğini al ve düzenleme sayfasına gönder
        html_content = extract_text_and_images_from_pdf(article.file.path)
        return render(request, "revize_et.html", {
            "article": article,
            "pdf_content": html_content,  # PDF içeriğini şablona gönder
        })






from django.http import Http404, FileResponse

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


from PIL import Image

def generate_pdf_with_images_and_text(text, images, output_path):
    # PDF dosyasını oluştur
    c = canvas.Canvas(output_path, pagesize=letter)
    width, height = letter

    # Metni PDF'ye ekle
    c.setFont("Helvetica", 12)
    text_object = c.beginText(40, height - 40)
    text_object.textLines(text)
    c.drawText(text_object)

    # Resimleri PDF'ye ekle
    y_position = height - 100  # Başlangıç pozisyonu
    for img_path in images:
        img = Image.open(img_path)
        img_width, img_height = img.size
        aspect_ratio = img_height / float(img_width)
        img_width = 400  # Görselin genişliğini ayarla
        img_height = aspect_ratio * img_width
        c.drawImage(img_path, 40, y_position, width=img_width, height=img_height)
        y_position -= img_height + 20  # Bir sonraki resmin y pozisyonunu ayarla

    # PDF'i kaydet
    c.save()

import spacy
from collections import Counter

# spaCy dil modeli yükleniyor
nlp = spacy.load("en_core_web_sm")

from django.shortcuts import render, get_object_or_404
from .models import User, ReviewerSubtopic
from collections import defaultdict

def hakem_page(request, hakem_id):

    # Hakemi ID'ye göre al
    hakem = User.objects.filter(username__startswith=hakem_id).first()

    # Hakemin yaptığı incelemeleri al
    reviewers = ReviewerSubtopic.objects.filter(reviewer=hakem).select_related('subtopic')

    grouped_reviewers = defaultdict(list)

    for entry in reviewers:
        grouped_reviewers[entry.reviewer.username].append(entry.subtopic.name)

    # JSON formatına uygun çıktı
    grouped_result = [{"reviewer": reviewer, "subtopics": subtopics} for reviewer, subtopics in
                      grouped_reviewers.items()]

    # Hakemin bilgileriyle şablonu render et
    return render(request, 'hakem_page.html', {
        'hakem': hakem,
        'reviewers': grouped_result,
    })



import spacy


# SpaCy modelini yükleyin
nlp = spacy.load("en_core_web_sm")

# Şifreleme için Fernet anahtarını oluşturun (Bu anahtar bir kez oluşturulup güvenli bir yerde saklanmalıdır)
# Anahtarınızı güvenli bir şekilde saklayın (örneğin, çevresel değişkenlerde).
from cryptography.fernet import Fernet
from django.conf import settings

from cryptography.fernet import Fernet

# Anahtarı çevresel değişkenden al
key = settings.FERNET_KEY.encode()  # Anahtarın byte formatına çevrilmesi gerekebilir
cipher_suite = Fernet(key)

from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Article

def encrypt_article(request, article_id):
    article = Article.objects.get(id=article_id)

    # Yazar ve kurum isimlerini belirle
    sensitive_words = ['Yazar', 'Kurum']  # Buraya daha fazla özel kelime ekleyebilirsiniz
    encrypted_content = article.content

    for word in sensitive_words:
        # Bu kelimeleri şifrele ve içeriğe yansıt
        encrypted_word = encrypt_word(word)
        encrypted_content = encrypted_content.replace(word, encrypted_word)

    # Şifreli içeriği kaydet
    article.encrypted_content = encrypted_content
    article.save()

    # Başarı mesajı ve yönlendirme
    messages.success(request, "Makale başarıyla şifrelendi!")
    return redirect('view_encrypted_article', article_id=article.id)

def encrypt_word(word):
    """Kelimeyi şifreler"""
    key = settings.FERNET_KEY
    cipher_suite = Fernet(key)
    encrypted = cipher_suite.encrypt(word.encode())
    return encrypted.decode()

from django.http import HttpResponse
import os

from django.http import HttpResponse

from django.http import HttpResponse
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from .models import Article


def download_encrypted_article(request, article_id):
    # Makale verisini al
    article = Article.objects.get(id=article_id)

    # Şifreli içerik al
    content = article.encrypted_content if article.encrypted_content else article.content

    # HTTP yanıtını oluştur
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{article.title}_encrypted.pdf"'

    # PDF oluşturma
    p = canvas.Canvas(response, pagesize=letter)
    width, height = letter

    # Başlık yazdır
    p.setFont("Helvetica-Bold", 14)
    p.drawString(100, height - 40, f"Makale Başlığı: {article.title}")

    # Şifreli içeriği yazdır
    p.setFont("Helvetica", 10)
    text_object = p.beginText(100, height - 60)
    text_object.setFont("Helvetica", 10)
    text_object.setTextOrigin(100, height - 60)

    # Şifreli içeriği sayfaya ekle (satır satır ekleniyor)
    lines = content.splitlines()
    for line in lines:
        text_object.textLine(line)

    p.drawText(text_object)
    p.showPage()
    p.save()

    return response


from django.shortcuts import get_object_or_404, render


from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from cryptography.fernet import Fernet
from .models import Article
from django.conf import settings
import re


# Şifrelenmiş makaleyi görüntüleme
def view_encrypted_article(request, article_id):
    article = Article.objects.get(id=article_id)

    # Eğer şifreli içerik varsa, onu al
    content = article.encrypted_content if article.encrypted_content else article.content
    print(f"Makale içeriği: {content}")  # Debugging için ekledik

    # İçeriği şablona gönder
    return render(request, 'view_encrypted_article.html', {'content': content, 'article': article})





