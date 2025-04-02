from collections import Counter
from random import random
import re


def pdf_to_text(pdf_path, txt_path, tracking_number):
    """
    PDF içeriğini çıkararak bir TXT dosyasına kaydeder. Ayrıca PDF'deki resimleri tanıyıp
    her bir resme benzersiz bir isim verir ve bu isimleri metne ekler.
    """
    # PDF dosyasını aç
    doc = fitz.open(pdf_path)
    text_content = ""
    image_counter = 1  # Resim sırası
    image_references = []  # Resim referansları (metne eklenecek)

    # PDF'deki her sayfa üzerinde döngü
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

import random  # random modülünü içe aktarın

def generate_tracking_number():
    """
    5 basamaklı benzersiz bir takip numarası oluşturur.
    """
    while True:
        tracking_number = str(random.randint(10000, 99999))
        if not Article.objects.filter(tracking_number=tracking_number).exists():
            return tracking_number



from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from PIL import Image
import os


def generate_pdf_with_images_and_text(text, images, output_path):
    """Metin ve resim içeren bir PDF oluşturur."""
    c = canvas.Canvas(output_path, pagesize=letter)
    width, height = letter

    c.setFont("Helvetica", 12)
    text_object = c.beginText(40, height - 40)
    text_object.textLines(text)
    c.drawText(text_object)

    y_position = height - 100
    for img_path in images:
        img = Image.open(img_path)
        img_width, img_height = img.size
        aspect_ratio = img_height / float(img_width)
        img_width = 400
        img_height = aspect_ratio * img_width
        c.drawImage(img_path, 40, y_position, width=img_width, height=img_height)
        y_position -= img_height + 20

    c.save()


from .models import Article  # Makale modeli


from django.conf import settings

import re
import spacy
import os
import fitz  # PyMuPDF

# SpaCy dil modelini yükleyelim
nlp = spacy.load("en_core_web_lg")


def extract_person_info(text):
    """Başlık ve abstract arasında geçen kişi isimlerini, kurumlarını ve e-posta adreslerini tespit eder."""
    # Abstract bölümünün başlangıcını bul
    abstract_match = re.search(r'\babstract\b', text, re.IGNORECASE)
    abstract_index = abstract_match.start() if abstract_match else len(text)
    pre_abstract_text = text[:abstract_index]  # Abstract öncesindeki metin

    doc = nlp(pre_abstract_text)
    persons = set()
    institutions = set()
    emails = set(re.findall(r'\S+@\S+', pre_abstract_text))  # E-posta adreslerini bul

    # Kişi isimlerini tespit et
    for ent in doc.ents:
        if ent.label_ == "PERSON":
            persons.add(ent.text)

        # Kurum bilgisini tespit et (Organizasyonlar: ORG etiketi)
        if ent.label_ == "ORG":  # "ORG" etiketi, organizasyonları belirtir
            if not any(word in ent.text for word in ["Network", "Computer", "IEEE", "Department", "Engineering"]):
                institutions.add(ent.text)

    # Kişisel bilgileri şifreleyin (isteğe bağlı)
    encrypted_persons = {person: encrypt_data(person) for person in persons}
    encrypted_institutions = {institution: encrypt_data(institution) for institution in institutions}
    encrypted_emails = {email: encrypt_data(email) for email in emails}

    return encrypted_persons, encrypted_institutions, encrypted_emails, pre_abstract_text



import fitz  # PyMuPDF
import re
import os
from django.conf import settings

def process_and_save_pdf(article):
    """PDF üzerindeki yazar bilgilerini tespit edip şifreleyerek kaydeder."""
    original_pdf_path = article.file.path
    doc = fitz.open(original_pdf_path)

    # İlk sayfadaki bilgileri al
    first_page_text = doc[0].get_text("text")
    persons, institutions, emails, pre_abstract_text = extract_person_info(first_page_text)

    # Tüm sansürlenecek kelimeleri birleştiriyoruz
    sensitive_info_set = persons | institutions | emails

    encrypted_folder = os.path.join(settings.MEDIA_ROOT, "encrypted_articles")
    os.makedirs(encrypted_folder, exist_ok=True)
    censored_pdf_path = os.path.join(encrypted_folder, f"{article.tracking_number}_censored.pdf")

    for page in doc:
        text = page.get_text("text")

        for sensitive_info in sensitive_info_set:
            encrypted_info = encrypt_data(sensitive_info.encode('utf-8'))  # Şifrelenmiş veri
            regex = re.compile(re.escape(sensitive_info), re.IGNORECASE)
            areas = page.search_for(sensitive_info)

            if areas:  # Eğer eşleşme bulunduysa
                for rect in areas:
                    page.add_redact_annot(rect, fill=(0, 0, 0))  # Siyah sansür ekle
                page.add_text_annot(areas[0], encrypted_info)  # Şifrelenmiş metni ekle

        page.apply_redactions()  # Redaksiyonları uygula

    doc.save(censored_pdf_path)
    return censored_pdf_path



def get_name_from_email(email):
    """E-posta adresinden kişi ismi çıkarmak için basit bir fonksiyon."""
    # E-posta adresinden '@' öncesindeki kısmı al (örn: anubhav2901@gmail.com -> anubhav2901)
    name_part = email.split('@')[0]
    name_parts = name_part.split('.')

    # E-posta adresinde isme dair bir şey varsa, sadece ilk harfleri büyük yapıp döndürelim
    if len(name_parts) > 1:
        return ' '.join([part.capitalize() for part in name_parts])
    return name_part.capitalize()  # E-posta adresinde sadece bir parça varsa, onu döndürelim


def extract_person_names_from_text(text):
    """Abstract öncesindeki metinden tüm kişi isimlerini çıkarır."""
    doc = nlp(text)
    person_names = set()

    # Kişi isimlerini tespit et
    for ent in doc.ents:
        if ent.label_ == "PERSON":
            person_names.add(ent.text)

    return person_names


from Crypto.Cipher import AES
from base64 import b64encode, b64decode
import os

from Crypto.Cipher import AES
from Crypto.Protocol.KDF import PBKDF2
from base64 import b64encode, b64decode
import os

# Sabit bir şifreleme anahtarı üretmek için PBKDF2 kullanıyoruz.
SECRET_KEY = "my_secret_passphrase"  # Daha güvenli olması için çevresel değişkenlere taşınabilir
SALT = b'\x12\x34\x56\x78\x90\xab\xcd\xef'  # Sabit bir salt

key = PBKDF2(SECRET_KEY, SALT, dkLen=32)  # AES-256 için 32 byte key üretimi


def encrypt_data(data):
    """Veriyi AES ile şifreler ve Base64 olarak döndürür."""
    if isinstance(data, str):
        data = data.encode('utf-8')  # Eğer `str` ise `bytes`'a çevir
    elif isinstance(data, bytes):
        pass  # Zaten `bytes`, ek bir işlem yapmaya gerek yok

    cipher = AES.new(key, AES.MODE_EAX)
    ciphertext, tag = cipher.encrypt_and_digest(data)
    encrypted_data = cipher.nonce + tag + ciphertext
    return b64encode(encrypted_data).decode('utf-8')


def decrypt_data(encrypted_data):
    """Şifreli veriyi çözerek orijinal haline döndürür."""
    encrypted_data = b64decode(encrypted_data)
    nonce = encrypted_data[:16]
    tag = encrypted_data[16:32]
    ciphertext = encrypted_data[32:]

    cipher = AES.new(key, AES.MODE_EAX, nonce=nonce)
    return cipher.decrypt_and_verify(ciphertext, tag).decode('utf-8')
