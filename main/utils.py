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




import fitz  # PyMuPDF
import os
import re
import spacy
from django.conf import settings
from django.shortcuts import get_object_or_404, redirect
from .models import Article  # Makale modeli

import fitz  # PyMuPDF
import os
import re
import spacy
from django.conf import settings
from django.shortcuts import get_object_or_404, redirect
from .models import Article  # Makale modeli

import re
import os
import fitz  # PyMuPDF
import spacy
from django.conf import settings

# SpaCy modelini yükle
import re
import os
import fitz  # PyMuPDF
import spacy
from django.conf import settings

import re
import os
import fitz  # PyMuPDF
import spacy
from django.conf import settings
import re
import os
import fitz  # PyMuPDF
import spacy
from django.conf import settings

import re
import os
import fitz  # PyMuPDF
import spacy
from django.conf import settings
import spacy
import re
import fitz  # PyMuPDF
import os

# Daha güçlü bir model kullanıyoruz
nlp = spacy.load("en_core_web_trf")  # Transformer tabanlı model

# Sansürlenmeyecek teknik terimler ve method isimleri
IEEE_HEADINGS = {
    "Emotion Recognition", "Neural Network", "Short-Time Fourier Transform",
    "CNN", "LSTM", "Support Vector Machine", "Deep Learning", "Artificial Intelligence",
    "INTRODUCTION","DATASET ON EMOTION WITH NATURALISTICSTIMULI (DENS)",
    "METHODOLOGY","RESULTS","DISCUSSION","CONCLUSION","ACKNOWLEDGMENT",
    "REFERENCES",
}

def is_heading(line):
    """
    Satırın IEEE başlıklarından biri olup olmadığını kontrol eder.
    - Sadece büyük harf olup olmadığına bakmaz, belirlenen IEEE başlıklarıyla kıyaslar.
    """
    line = line.strip()
    for heading in IEEE_HEADINGS:
        if line.lower().startswith(heading.lower()):
            return True
    return False

def extract_sensitive_info(text):
    """
    Abstract kısmına kadar olan bölümden yazar isimlerini, özel kurum isimlerini ve e-posta adreslerini tespit eder.
    - IEEE formatına uygun başlıklar ve teknik terimler sansürlenmez.
    - Referans kısmı sansürlenmez.
    """

    # REFERENCES bölümünü belirleyelim (sansürlememek için)
    references_match = re.search(r'\bReferences\b', text, re.IGNORECASE)
    references_index = references_match.start() if references_match else len(text)
    pre_references_text = text[:references_index]  # References kısmından önceki metni al

    # Abstract'ı büyük/küçük harf duyarsız aramak için
    abstract_match = re.search(r'\babstract\b', pre_references_text, re.IGNORECASE)
    abstract_index = abstract_match.start() if abstract_match else len(pre_references_text)
    pre_abstract_text = pre_references_text[:abstract_index]  # Abstract kısmından önceki metni al

    # Satır satır bölerek başlıkları belirleyelim
    lines = pre_abstract_text.split("\n")
    headings = {line.strip() for line in lines if is_heading(line)}

    # SpaCy ile özel isimleri (yazar ve özel isim içeren kurum adları) bul
    doc = nlp(pre_abstract_text)
    sensitive_info = set()

    for ent in doc.ents:
        # Eğer tespit edilen varlık bir başlıksa sansürleme!
        if ent.text.strip() in headings:
            continue

        # Teknik terimler sansürlenmemeli
        if ent.text in IEEE_HEADINGS:
            continue

        if ent.label_ == "PERSON":  # Yazar isimlerini ekle
            sensitive_info.add(ent.text)

        elif ent.label_ == "ORG":  # Kurum adlarındaki özel isimleri sansürle
            org_words = ent.text.split()
            filtered_org = []
            for word in org_words:
                word_doc = nlp(word)
                if any(sub_ent.label_ == "PERSON" for sub_ent in word_doc.ents):
                    filtered_org.append("[REDACTED]")  # Sadece özel isimleri sansürle
                else:
                    filtered_org.append(word)
            redacted_org = " ".join(filtered_org)
            if redacted_org != ent.text:
                sensitive_info.add(ent.text)  # Orijinal metni sansürlenecek listeye ekle
                sensitive_info.add(redacted_org)  # Sansürlenmiş hali de listeye eklensin

    # Regex ile yazar isimlerini daha iyi yakalamak için ek analiz
    name_regex = r"\b[A-Z][a-z]+(?:\s[A-Z][a-z]+){1,2}\b"  # 2 veya 3 kelimelik isimleri bul
    possible_names = re.findall(name_regex, pre_abstract_text)

    for name in possible_names:
        if name not in headings and name not in IEEE_HEADINGS:  # Başlıklara ve teknik terimlere dokunma
            sensitive_info.add(name)

    # Regex ile e-posta adreslerini bul
    email_regex = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
    emails = re.findall(email_regex, pre_abstract_text)
    sensitive_info.update(emails)  # Set'e eklendiği için tekrar eden değerler otomatik olarak filtrelenir

    return sensitive_info

def process_and_save_pdf(article):
    """PDF üzerindeki yazar isimlerini, kurum isimlerini (sadece özel isimleri) ve e-posta adreslerini sansürleyerek kaydeder."""
    original_pdf_path = article.file.path  # Orijinal PDF dosyasının yolu
    doc = fitz.open(original_pdf_path)

    # Sansürlü PDF'yi kaydetmek için yeni bir klasör oluştur
    encrypted_folder = os.path.join(settings.MEDIA_ROOT, "encrypted_articles")
    os.makedirs(encrypted_folder, exist_ok=True)

    censored_pdf_path = os.path.join(encrypted_folder, f"{article.tracking_number}_censored.pdf")

    for page in doc:  # PDF'in her sayfası için işlemi uygula
        text = page.get_text("text")  # Sayfa metnini al
        sensitive_info_list = extract_sensitive_info(text)  # Hassas bilgileri tespit et

        for sensitive_info in sensitive_info_list:
            areas = page.search_for(sensitive_info)  # Sayfa içinde bilgilerin geçtiği yerleri bul

            for rect in areas:
                page.add_redact_annot(rect, fill=(0, 0, 0))  # Siyah kutu ile sansürle

        page.apply_redactions()  # Sansürleri uygula

    doc.save(censored_pdf_path)  # Yeni sansürlenmiş PDF'yi kaydet
    return censored_pdf_path
