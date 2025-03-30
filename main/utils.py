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

# SpaCy'nin büyük modelini yükle
import re
import os
import spacy
import fitz  # PyMuPDF
from django.conf import settings

# SpaCy dil modelini yükleyelim
import re
import os
import spacy
import fitz  # PyMuPDF
from django.conf import settings

# SpaCy dil modelini yükleyelim
import re
import os
import spacy
import fitz  # PyMuPDF
from django.conf import settings
import re
import os
import spacy
import fitz  # PyMuPDF
from django.conf import settings

# SpaCy dil modelini yükleyelim
import re
import os
import spacy
import fitz  # PyMuPDF
from django.conf import settings

# SpaCy dil modelini yükleyelim
import re
import os
import spacy
import fitz  # PyMuPDF
from django.conf import settings

import re
import os
import spacy
import fitz  # PyMuPDF
from django.conf import settings

import re
import spacy
import os
import fitz  # PyMuPDF

# SpaCy dil modelini yükleyelim
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
    for ent in doc.ents:
        if ent.label_ == "ORG":  # "ORG" etiketi, organizasyonları belirtir
            if not any(word in ent.text for word in ["Network", "Computer","IEEE"]):
                institutions.add(ent.text)

    return persons, institutions, emails

def process_and_save_pdf(article):
    """PDF üzerindeki yazar bilgilerini tespit edip sansürleyerek kaydeder."""
    original_pdf_path = article.file.path
    doc = fitz.open(original_pdf_path)

    # İlk sayfadaki bilgileri al
    first_page_text = doc[0].get_text("text")
    persons, institutions, emails = extract_person_info(first_page_text)

    # Sansürlü PDF'yi kaydetmek için yeni klasör oluştur
    encrypted_folder = os.path.join(settings.MEDIA_ROOT, "encrypted_articles")
    os.makedirs(encrypted_folder, exist_ok=True)

    censored_pdf_path = os.path.join(encrypted_folder, f"{article.tracking_number}_censored.pdf")

    # İlk 5 satırı atla ve sansürle
    for page in doc:
        text = page.get_text("text")
        lines = text.split("\n")

        # İlk 5 satırı atla
        lines_to_process = lines[5:]

        # İşlenecek metni birleştir
        text_to_process = "\n".join(lines_to_process)

        # Sadece tespit edilen kişi isimleri, kurumları ve e-posta adreslerini sansürle
        for sensitive_info in persons | institutions | emails:
            areas = page.search_for(sensitive_info)
            for rect in areas:
                page.add_redact_annot(rect, fill=(0, 0, 0))  # Siyah renk ile sansürle

        page.apply_redactions()

    doc.save(censored_pdf_path)
    return censored_pdf_path
