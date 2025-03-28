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
from collections import Counter

# spaCy dil modeli yükleniyor
nlp = spacy.load("en_core_web_sm")


from .models import *

from django.conf import settings

from PIL import Image, ImageFilter
from .models import Article  # Makale modeli
import spacy

# SpaCy modelini yükle
nlp = spacy.load("en_core_web_sm")


import fitz  # PyMuPDF
import os


import re

import fitz  # PyMuPDF
import re
import os


# Yazar adlarını ve kurum bilgilerini tespit etmek için kullanılacak regex
def extract_author_names(text):
    """Yazar isimlerini başlık ve yazar kısmından tespit eder."""
    author_regex = r"\b[A-Z][a-z]+(?:\s[A-Z][a-z]+)+\b"  # Basit bir yazar adı regex örneği
    authors = re.findall(author_regex, text)
    return authors


def censor_text(text, author_list):
    """Metni sansürler ve yazar isimlerini '[SANSÜRLEDİ]' ile değiştirir."""
    censored_text = text
    for author in author_list:
        censored_text = censored_text.replace(author, "[SANSÜRLEDİ]")
    return censored_text


def process_and_save_pdf(article, output_folder):
    """PDF dosyasındaki yazar isimlerini sansürler ve yeni PDF dosyasını kaydeder."""
    original_pdf_path = article.file.path  # Orijinal PDF dosyasının yolu
    doc = fitz.open(original_pdf_path)

    encrypted_folder = os.path.join(output_folder, "encrypted_articles")
    os.makedirs(encrypted_folder, exist_ok=True)  # Klasör yoksa oluştur

    censored_pdf_path = os.path.join(encrypted_folder, f"{article.tracking_number}_encrypted.pdf")
    pdf_writer = fitz.open()

    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        text = page.get_text("text")

        # Yazar isimlerini çıkarmak
        author_list = extract_author_names(text)

        # Yazar isimlerini sansürlemek
        censored_text = censor_text(text, author_list)

        # Yeni sayfa oluşturmak
        new_page = pdf_writer.new_page(width=page.rect.width, height=page.rect.height)
        new_page.insert_text((72, 72), censored_text, fontsize=12, color=(0, 0, 0))

    # Sansürlenmiş PDF'i kaydet
    pdf_writer.save(censored_pdf_path)
    return censored_pdf_path


def extract_author_names(text):
    """Yazar isimlerini büyük harflerle yazılmış şekilde tespit eder."""
    author_pattern = r"\b[A-Z]+(?: [A-Z]+)+\b"  # Büyük harflerle yazılmış yazar isimlerini tespit eder
    authors = re.findall(author_pattern, text)
    return set(authors)


def censor_text(text, author_list):
    """Metindeki büyük harflerle yazılmış yazar isimlerini sansürler."""
    for author in author_list:
        text = re.sub(rf"\b{re.escape(author)}\b", "[SANSÜRLÜ]", text)
    return text
