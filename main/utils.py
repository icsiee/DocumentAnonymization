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


import spacy

nlp = spacy.load("en_core_web_sm")


from .models import *

from PIL import Image, ImageFilter

# SpaCy modelini yükle
nlp = spacy.load("en_core_web_sm")


import fitz  # PyMuPDF
import os


import re

import fitz  # PyMuPDF
import re
import os


# Yazar adlarını ve kurum bilgilerini tespit etmek için kullanılacak regex
import fitz  # PyMuPDF
import re
import os
import fitz  # PyMuPDF
import os
import re
from django.conf import settings
from django.shortcuts import get_object_or_404, redirect
from .models import Article  # Makale modeli

def extract_author_names(text):
    """PDF içindeki yazar isimlerini büyük harf formatına göre tespit eder."""
    author_pattern = r"\b[A-Z]+(?: [A-Z]+)+\b"  # Büyük harfli kelime gruplarını bul
    authors = set(re.findall(author_pattern, text))
    return authors

def process_and_save_pdf(article):
    """PDF üzerindeki yazar isimlerini sansürleyerek kaydeder."""
    original_pdf_path = article.file.path  # Orijinal PDF dosyasının yolu
    doc = fitz.open(original_pdf_path)

    # Sansürlü PDF'yi kaydetmek için yeni bir klasör oluştur
    encrypted_folder = os.path.join(settings.MEDIA_ROOT, "encrypted_articles")
    os.makedirs(encrypted_folder, exist_ok=True)

    censored_pdf_path = os.path.join(encrypted_folder, f"{article.tracking_number}_censored.pdf")

    for page in doc:  # PDF'in her sayfası için işlemi uygula
        text = page.get_text("text")  # Sayfa metnini al
        author_list = extract_author_names(text)  # Yazar isimlerini tespit et

        for author in author_list:
            areas = page.search_for(author)  # Sayfa içinde yazar isminin geçtiği yerleri bul

            for rect in areas:
                page.add_redact_annot(rect, fill=(0, 0, 0))  # Siyah kutu ile sansürle

        page.apply_redactions()  # Sansürleri uygula

    doc.save(censored_pdf_path)  # Yeni sansürlenmiş PDF'yi kaydet
    return censored_pdf_path