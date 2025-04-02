from . import apps
from .forms import *

from django.views.decorators.csrf import csrf_exempt
from .utils import *
import spacy



import torch
from transformers import BertTokenizer, BertModel
from sklearn.metrics.pairwise import cosine_similarity

from django.contrib.auth import get_user_model

User = get_user_model()  # Kullanıcı modelini al

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

from .models import *


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


from django.contrib.auth import get_user_model

User = get_user_model()

def editor_page(request):
    """Editör sayfası işlemleri (Bu fonksiyon yalnızca bir defa çalışacaktır)"""

    # Eğer daha önce atama yapıldıysa tekrar çalıştırma
    if ReviewerSubtopic.objects.exists():
        return render(request, 'editor.html', {
            'editor_messages': Message.objects.filter(receiver__username='editör@gmail.com').order_by('-sent_date'),
            'articles': Article.objects.all(),
            'logs':Log.objects.all(),
            'reviewers': User.objects.filter(user_type='Hakem'),
            'reviewer_subtopics': ReviewerSubtopic.objects.select_related('reviewer', 'subtopic').all()
        })

    # 1️⃣ Editör, makaleler ve mesajları al
    articles = Article.objects.all()

    # Editör kullanıcısını oluştur
    editor, created = User.objects.get_or_create(
        username='editör@gmail.com',
        defaults={"user_type": "Editör", "email": 'editör@gmail.com'}
    )

    # Editör mesajlarını al
    editor_messages = Message.objects.filter(receiver=editor).order_by('-sent_date')

    # 2️⃣ Hakemleri oluştur (13 hakem)
    reviewer_users = []
    for i in range(1, 14):
        reviewer, created = User.objects.get_or_create(
            username=f"hakem{i}",
            defaults={"user_type": "Hakem", "email": f"hakem{i}@gmail.com"}
        )
        reviewer_users.append(reviewer)

    # 3️⃣ Alt başlıkları oluştur
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

    subtopics = []
    for subtopic_name, main_topic in TOPIC_MAP:
        subtopic, created = Subtopic.objects.get_or_create(
            name=subtopic_name,
            defaults={"main_topic": main_topic}
        )
        subtopics.append(subtopic)

    # 4️⃣ Her hakeme rastgele 2 veya 3 alt başlık ata
    random.shuffle(subtopics)  # Konuları karıştır
    assignments = {reviewer: [] for reviewer in reviewer_users}  # Hakem-atama sözlüğü

    # Önce her alt başlık için en az bir hakem ata
    for i, subtopic in enumerate(subtopics):
        reviewer = reviewer_users[i % len(reviewer_users)]  # Dönerek sırayla atama yap
        ReviewerSubtopic.objects.get_or_create(reviewer=reviewer, subtopic=subtopic)
        assignments[reviewer].append(subtopic)

    # Hakemlere 2 veya 3 konu verilecek şekilde ek atamalar yap
    for reviewer in reviewer_users:
        while len(assignments[reviewer]) < 2 or (len(assignments[reviewer]) < 3 and random.choice([True, False])):
            available_subtopics = [s for s in subtopics if s not in assignments[reviewer]]
            if not available_subtopics:
                break  # Eğer atayacak başka konu kalmadıysa dur
            subtopic = random.choice(available_subtopics)
            ReviewerSubtopic.objects.get_or_create(reviewer=reviewer, subtopic=subtopic)
            assignments[reviewer].append(subtopic)

    # 5️⃣ Başarılı mesajı gönder
    messages.success(request, "Hakemler ve konular başarıyla oluşturuldu ve atandı!")
    articles = Article.objects.prefetch_related('articlesubtopic_set__subtopic').all()

    # 6️⃣ Atamaları veriye ekleyerek sayfayı render et
    return render(request, 'editor.html', {
        'editor_messages': editor_messages,
        'articles': articles,
        'reviewers': reviewer_users,
        'reviewer_subtopics': ReviewerSubtopic.objects.select_related('reviewer', 'subtopic').all()
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


def determine_article_topics_bert(article):
    """
    Makalenin içeriğini analiz ederek ilgili alt başlıkları belirler.
    Her durumda en az bir alt başlık ataması yapılmasını sağlar.
    """
    subtopics = Subtopic.objects.all()  # Tüm alt başlıkları al
    matched_subtopics = []

    # Basit eşleşme ile alt başlıkları bulmaya çalışıyoruz
    for subtopic in subtopics:
        if subtopic.name.lower() in article.content.lower():  # Basit eşleşme
            matched_subtopics.append(subtopic)

    # Eğer eşleşen alt başlık yoksa, en azından bir alt başlık atayalım
    if not matched_subtopics:
        # Burada "Deep Learning" gibi bir alt başlık belirliyoruz, tercihe göre başka bir şey seçilebilir
        general_subtopic = Subtopic.objects.get_or_create(name="Deep Learning")[0]
        matched_subtopics.append(general_subtopic)

    return matched_subtopics

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding
import os
from django.core.exceptions import ObjectDoesNotExist

def encrypt_pdf(file_path, key):
    """
    PDF dosyasını AES ile şifreler.
    """
    # Dosya açılır ve içerik okunur
    with open(file_path, 'rb') as f:
        data = f.read()

    # AES için 16 baytlık bir iv (Initialization Vector) oluşturuluyor
    iv = os.urandom(16)

    # Veriyi AES ile şifreleme
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    encryptor = cipher.encryptor()

    # Veri padding işlemi
    padder = padding.PKCS7(algorithms.AES.block_size).padder()
    padded_data = padder.update(data) + padder.finalize()

    # Şifreli veri ve IV dosyaya yazılır
    encrypted_data = encryptor.update(padded_data) + encryptor.finalize()

    encrypted_file_path = file_path + '.enc'
    with open(encrypted_file_path, 'wb') as f:
        f.write(iv + encrypted_data)  # IV ve şifreli veri birlikte kaydedilir

    return encrypted_file_path


from .utils import *

def makale_yukle(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        title = request.POST.get('title')

        if not email or not title:
            messages.error(request, "Lütfen tüm alanları doldurun.")
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

            # Yolu doğru bir şekilde oluştur
            pdf_path = os.path.join(settings.MEDIA_ROOT, 'articles', pdf_filename)
            txt_path = os.path.join(settings.MEDIA_ROOT, 'text', txt_filename)

            # Dosyayı kaydet
            with open(pdf_path, 'wb') as destination:
                for chunk in makale.chunks():
                    destination.write(chunk)

            # PDF içeriğini çıkarıp TXT olarak kaydet
            extracted_text = pdf_to_text(pdf_path, txt_path, tracking_number)

            # Makaleyi kaydet
            article = Article.objects.create(
                title=title,
                author=user,
                file=f"articles/{pdf_filename}",
                tracking_number=tracking_number,
                content=extracted_text
            )

            # Alt başlıkları kaydet
            matched_subtopics = determine_article_topics_bert(article)
            for subtopic in matched_subtopics:
                ArticleSubtopic.objects.get_or_create(article=article, subtopic=subtopic)

            # Log kaydı ekle
            Log.objects.create(
                action=f"Makale Yüklendi: {title}",
                user=user
            )

            messages.success(request, f"Makale başarıyla yüklendi! Takip Numaranız: {tracking_number}")
            return redirect('yazar_sayfasi')

        else:
            messages.error(request, "Lütfen yalnızca PDF formatında dosya yükleyin!")

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


import os
import shutil
from django.conf import settings
from django.shortcuts import redirect, render
from django.contrib import messages
from django.apps import apps
from .models import Article

def delete_all_articles(request):
    if request.method == "POST":
        # 1️⃣ Tüm makaleleri sil
        articles = Article.objects.all()
        for article in articles:
            if article.file:
                article_file_path = os.path.join(settings.MEDIA_ROOT, article.file.name)
                if os.path.exists(article_file_path):
                    try:
                        os.remove(article_file_path)
                        messages.success(request, f"{article_file_path} başarıyla silindi.")
                    except Exception as e:
                        messages.error(request, f"Dosya silinirken hata oluştu: {str(e)}")

            article.delete()

        # 2️⃣ Tüm veritabanı tablolarını temizle
        for model in apps.get_models():
            model.objects.all().delete()  # Her tablodaki tüm verileri sil

        # 3️⃣ Belirtilen medya klasörlerini temizle
        folders_to_clear = ['images', 'articles', 'text', 'encrypted_articles']
        for folder in folders_to_clear:
            folder_path = os.path.join(settings.MEDIA_ROOT, folder)
            if os.path.exists(folder_path):
                try:
                    for filename in os.listdir(folder_path):
                        file_path = os.path.join(folder_path, filename)
                        if os.path.isfile(file_path) or os.path.islink(file_path):
                            os.unlink(file_path)
                        elif os.path.isdir(file_path):
                            shutil.rmtree(file_path)

                    messages.success(request, f"{folder} klasörü başarıyla temizlendi.")
                except Exception as e:
                    messages.error(request, f"{folder} klasörü temizlenirken hata oluştu: {str(e)}")

        messages.success(request, "Tüm veritabanı kayıtları ve medya dosyaları başarıyla silindi.")
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

from django.shortcuts import render, get_object_or_404
from .models import User, ReviewerSubtopic
from collections import defaultdict

from django.shortcuts import render, get_object_or_404
from .models import User


def hakem_page(request, hakem_username):
    """Hakem sayfası işlemleri"""
    reviewer = get_object_or_404(User, username=hakem_username, user_type='Hakem')

    # Hakemin atanan konuları
    reviewer_subtopics = ReviewerSubtopic.objects.filter(reviewer=reviewer)
    assignment= Assignment.objects.filter(reviewer=reviewer)
    return render(request, 'hakem_page.html', {
        'reviewer': reviewer,
        'reviewer_subtopics': reviewer_subtopics,
        'assignment': assignment,
    })


import spacy


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


def encrypt_word(word):
    """Kelimeyi şifreler"""
    key = settings.FERNET_KEY
    cipher_suite = Fernet(key)
    encrypted = cipher_suite.encrypt(word.encode())
    return encrypted.decode()


from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

from cryptography.fernet import Fernet


# Şifrelenmiş makaleyi görüntüleme
def view_encrypted_article(request, article_id):
    article = Article.objects.get(id=article_id)

    # Eğer şifreli içerik varsa, onu al
    content = article.encrypted_content if article.encrypted_content else article.content
    print(f"Makale içeriği: {content}")  # Debugging için ekledik

    # İçeriği şablona gönder
    return render(request, 'view_encrypted_article.html', {'content': content, 'article': article})


from PIL import Image, ImageFilter

from django.conf import settings
from django.shortcuts import render, redirect

import re

import fitz  # PyMuPDF


from .utils import process_and_save_pdf



def encrypt_article(request, article_id):
    """Makale PDF'sini şifreleyerek veya şifreyi kaldırarak günceller."""
    article = get_object_or_404(Article, id=article_id)

    if article.is_encrypted:
        # Makale zaten şifreli, şifreyi kaldır
        article.encrypted_content = None  # Şifreli içeriği temizle
        article.is_encrypted = False  # Durumu şifresiz yap
    else:
        # Makale şifreli değil, şifreleme işlemini gerçekleştir
        censored_pdf_path = process_and_save_pdf(article)
        article.encrypted_content = censored_pdf_path  # Şifreli içeriği kaydet
        article.is_encrypted = True  # Şifreleme durumunu güncelle

    article.save()

    return JsonResponse({
        'success': True,
        'article_id': article.id,
        'is_encrypted': article.is_encrypted
    })



from django.conf import settings

from django.http import Http404, FileResponse
from django.shortcuts import get_object_or_404
import os
from django.conf import settings

from django.http import Http404, FileResponse
import os
from django.conf import settings
from .models import Article

from django.http import Http404, FileResponse
import os
from django.conf import settings
from .models import Article

def pdf_goruntule(request, tracking_number):
    # Article'ı tracking_number ile al
    article = get_object_or_404(Article, tracking_number=tracking_number)

    # Makale durumu "Tamamlandı" ise güncellenmiş PDF'yi aç
    if article.status == 'Tamamlandı':
        # Makale tamamlandığı için sadece güncellenmiş PDF dosyasını açıyoruz
        file_path = os.path.join(settings.MEDIA_ROOT, 'updated_articles', f"{article.tracking_number}_updated.pdf")
    else:
        # Eğer makale "Tamamlanmadı"ysa şifreli ya da şifresiz dosyayı açıyoruz
        if article.is_encrypted:
            file_path = os.path.join(settings.MEDIA_ROOT, 'encrypted_articles', f"{article.tracking_number}_censored.pdf")
        else:
            file_path = os.path.join(settings.MEDIA_ROOT, 'articles', f"{article.tracking_number}.pdf")

    # Dosya var mı kontrol et
    if not os.path.exists(file_path):
        raise Http404(f"Dosya bulunamadı: {file_path}")

    # PDF'yi tarayıcıda açılması için "inline" olarak döndür
    response = FileResponse(open(file_path, 'rb'), content_type='application/pdf')

    # Tarayıcıda açılmasını sağlamak için "inline" değeri veriyoruz
    response['Content-Disposition'] = f'inline; filename="{article.tracking_number}.pdf"'

    # PDF başlığını kontrol et
    response['Content-Type'] = 'application/pdf'

    return response


import os

from django.http import FileResponse, Http404

def download_encrypted_pdf(request, article_id):
    try:
        article = Article.objects.get(id=article_id)
        encrypted_pdf_path = article.encrypted_pdf

        if not os.path.exists(encrypted_pdf_path):
            raise Http404("PDF dosyası bulunamadı.")

        # Şifrelenmiş PDF'yi indirmek için geri döner
        return FileResponse(open(encrypted_pdf_path, 'rb'), as_attachment=True, filename=os.path.basename(encrypted_pdf_path))

    except Article.DoesNotExist:
        raise Http404("Makale bulunamadı.")


import random

from .models import Article, ArticleSubtopic, ReviewerSubtopic, Subtopic

from .models import Article, Assignment, User, ArticleSubtopic, ReviewerSubtopic, Log
from django.http import HttpResponse


from django.contrib import messages
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse

def send_article_view(request, article_id):
    try:
        article = get_object_or_404(Article, id=article_id)

        # Eğer makale şifrelenmemişse, gönderme işlemini engelle
        if not article.is_encrypted:
            return HttpResponse("<h1>Bu makale şifrelenmediği için gönderme işlemi yapılamaz.</h1>")

        # Eğer makale zaten atanmışsa, tekrar atamaya izin verme
        if Assignment.objects.filter(article=article).exists():
            # Makale zaten atanmışsa, bildirim mesajı ekleyerek kullanıcıyı bilgilendir
            assigned_reviewer = Assignment.objects.get(article=article).reviewer
            messages.success(request, f"{article.title} makalesi zaten {assigned_reviewer.username} adlı hakeme atanmış.")
            return redirect("editor_page")  # Editör sayfasına yönlendirme

        # Makale ile ilişkili alt başlıkları al
        article_subtopics = ArticleSubtopic.objects.filter(article=article).values_list("subtopic", flat=True)

        # Hakemlerin listesine ulaş
        reviewers = User.objects.filter(user_type="Hakem")

        # Gönderilecek uygun hakemleri filtrele
        valid_reviewers = []
        for reviewer in reviewers:
            if ReviewerSubtopic.objects.filter(reviewer=reviewer, subtopic__in=article_subtopics).exists():
                valid_reviewers.append(reviewer)

        # Eğer uygun hakem varsa, bu hakemleri listele
        if not valid_reviewers:
            return HttpResponse("<h1>Bu makale için uygun hakem bulunamadı.</h1>")

        if request.method == "POST":
            reviewer_id = request.POST.get('reviewer_id')
            reviewer = get_object_or_404(User, id=reviewer_id, user_type="Hakem")

            # Atama işlemini gerçekleştir
            Assignment.objects.create(article=article, reviewer=reviewer)

            # Makale durumunu "İncelemede" olarak güncelle
            article.status = "İncelemede"
            article.save()

            # Log kaydını oluştur
            Log.objects.create(
                user=article.author,  # Makalenin yazarı (author) işlemi gerçekleştiren kullanıcıdır
                action=f"{article.title} makalesini {reviewer.username} adlı hakeme atama işlemi.",
                log_type='Bilgilendirme'
            )

            # Başarı mesajı gönder
            messages.success(request, f"{article.title} makalesi başarıyla {reviewer.username} adlı hakeme atandı.")

            return redirect("editor_page")  # Hakem atandıktan sonra editör sayfasına yönlendirme

        return render(request, 'article_detail.html', {
            'article': article,
            'valid_reviewers': valid_reviewers
        })

    except Exception as e:
        return HttpResponse(f"<h1>Bir hata oluştu: {e}</h1>")




from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from .models import Article, ReviewerSubtopic, Assignment
from django.contrib.auth.decorators import login_required

def assign_reviewer(request, article_id, reviewer_id):
    """
    Belirli bir hakemi belirli bir makaleye atayan fonksiyon.
    """
    print(reviewer_id)
    print("123")
    article = get_object_or_404(Article, id=article_id)
    reviewer_subtopic = get_object_or_404(ReviewerSubtopic, id=reviewer_id)
    reviewer=get_object_or_404(User, id=reviewer_subtopic.reviewer.id)
    editor = get_object_or_404(User, user_type='Editör')

    # Hakem zaten atanmışsa tekrar atamayı engelle
    if Assignment.objects.filter(article=article, reviewer=reviewer).exists():
        messages.warning(request, "Bu hakem zaten bu makaleye atanmış.")
    else:
        Assignment.objects.create(article=article, reviewer=reviewer, editor=editor)
        messages.success(request, f"{reviewer.username} hakemi başarıyla atandı!")

    return redirect('send_article', article_id=article.id)


def reviewer_dashboard(request):
    """
    Giriş yapan hakeme atanmış makaleleri listeleyen fonksiyon.
    """
    reviewer = get_object_or_404(ReviewerSubtopic, reviewer=request.user)
    assigned_articles = Assignment.objects.filter(reviewer=reviewer).select_related('article')

    context = {
        'assigned_articles': assigned_articles
    }
    return render(request, 'reviewer_dashboard.html', context)


from django.http import Http404, FileResponse
from django.shortcuts import get_object_or_404
import os
from django.conf import settings

def pdf_indir(request, tracking_number):
    # Makaleyi tracking_number ile al
    article = get_object_or_404(Article, tracking_number=tracking_number)

    # Eğer makale şifreliyse, şifreli versiyonu indirilecek
    if article.is_encrypted:
        file_path = os.path.join(settings.MEDIA_ROOT, 'encrypted_articles', f"{article.tracking_number}_censored.pdf")
    else:
        file_path = os.path.join(settings.MEDIA_ROOT, 'articles', f"{article.tracking_number}.pdf")

    # Dosya var mı kontrol et
    if not os.path.exists(file_path):
        raise Http404("İstenen dosya bulunamadı!")

    # PDF dosyasını indirme için sun
    response = FileResponse(open(file_path, 'rb'), content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{article.tracking_number}.pdf"'

    return response



from django.http import JsonResponse
from django.shortcuts import get_object_or_404
import os
from django.conf import settings
from .models import Article

def makale_sil(request, article_id):
    if request.method == "POST":
        article = get_object_or_404(Article, id=article_id)

        # Makaleyi veritabanından sil
        article.delete()

        return JsonResponse({"success": True})

    return JsonResponse({"success": False, "error": "Geçersiz istek"}, status=400)

# Logları görüntülemek için view fonksiyonu
from .models import Log  # Log modelinizi import edin

def log_panel(request):
    # Logları zaman sırasına göre sıralayın
    logs = Log.objects.all().order_by('-action_date')  # Yeni loglar en üstte olacak

    # Logları template'e gönderin
    return render(request, 'editor.html', {'logs': logs})


import os
import os
from django.conf import settings
from django.http import FileResponse, Http404
from django.shortcuts import get_object_or_404
from .models import Article

def pdf_goruntule_hakem(request, tracking_number):
    # Article'ı tracking_number ile al
    article = get_object_or_404(Article, tracking_number=tracking_number)

    # Hakemler yalnızca sansürlü makaleyi görebilir
    file_path = os.path.join(settings.MEDIA_ROOT, 'encrypted_articles', f"{article.tracking_number}_censored.pdf")

    # Dosya var mı kontrol et
    if not os.path.exists(file_path):
        raise Http404("Sansürlü makale bulunamadı.")

    # PDF'yi tarayıcıda açılması için "inline" olarak döndür
    response = FileResponse(open(file_path, 'rb'), content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="{article.tracking_number}_censored.pdf"'

    return response

# views.py

from django.shortcuts import render, get_object_or_404, redirect
from .models import Article, Review
from .forms import ReviewForm
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from .forms import ReviewForm
from .models import Article

import fitz  # PyMuPDF
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from .models import Article, Review


from django.shortcuts import render, get_object_or_404
from .models import Article, Review, Assignment
import fitz  # PyMuPDF

def review_article(request, article_id):
    article = get_object_or_404(Article, id=article_id)

    # Makaleye atanmış hakemi al
    try:
        assignment = Assignment.objects.get(article=article)
        reviewer = assignment.reviewer
    except Assignment.DoesNotExist:
        reviewer = None  # Eğer makaleye atanmış hakem yoksa

    # Yorum eklenmesi
    if request.method == 'POST':
        comment = request.POST.get('comment')
        if comment:
            # Yorum kaydetme
            review = Review.objects.create(
                article=article,
                reviewer=reviewer,  # Yorum yapan hakem burada atanıyor
                comment=comment
            )

            # Yorumları PDF'ye ekleyelim
            add_comment_to_pdf(article, comment)

            # Makale durumunu "Tamamlandı" olarak güncelle
            article.status = 'Tamamlandı'
            article.save()

            # Yorum ekledikten sonra kullanıcıyı aynı sayfaya yönlendir
            return render(request, 'review_article.html', {'article': article, 'review': review})

    return render(request, 'review_article.html', {'article': article})


import os
from django.conf import settings
import fitz  # PyMuPDF

def add_comment_to_pdf(article, comment):
    # PDF dosyasının kaydedileceği dizin
    updated_articles_dir = os.path.join(settings.MEDIA_ROOT, 'updated_articles')

    # Dizin yoksa, oluştur
    if not os.path.exists(updated_articles_dir):
        os.makedirs(updated_articles_dir)

    # Makalenin PDF dosyasını aç
    pdf_path = article.file.path  # Makalenin dosya yolu
    doc = fitz.open(pdf_path)

    # Son sayfayı al
    page = doc[-1]

    # Yorum metnini ekle
    text = f"\n\nYorum: {comment}"

    # Yorum ekleme
    page.insert_text((50, page.rect.height - 100), text, fontsize=12)

    # Yorum ekledikten sonra yeni PDF dosyasını kaydet
    new_pdf_path = os.path.join(updated_articles_dir, f"{article.tracking_number}_updated.pdf")
    doc.save(new_pdf_path)

    # Yeni PDF'yi kaydettik, dosya yolu döndürülebilir
    article.updated_pdf = new_pdf_path
    article.save()
