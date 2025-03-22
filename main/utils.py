from collections import Counter
from random import random

import fitz  # PyMuPDF
from django.shortcuts import render
from pyexpat.errors import messages

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from io import BytesIO

from main.models import Article
from main.views import nlp


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


def create_pdf_from_text(text, output_path):
    """
    Verilen metni alır ve PDF formatında belirtilen dosya yoluna kaydeder.
    :param text: PDF'ye dönüştürülmesi gereken metin
    :param output_path: Oluşturulacak PDF dosyasının kaydedileceği yol
    """
    # PDF dosyasını oluşturmak için bir bellek tamponu (buffer) kullanıyoruz.
    buffer = BytesIO()

    # PDF için canvas (tuval) oluşturuyoruz
    c = canvas.Canvas(buffer, pagesize=letter)  # letter boyutunda bir sayfa
    width, height = letter  # Sayfa genişliği ve yüksekliği (letter boyutu)

    # Yazı tipi ayarlıyoruz
    c.setFont("Helvetica", 10)  # Helvetica yazı tipi, 10 punto

    # Metni sayfaya eklemeye başlıyoruz
    text_object = c.beginText(40, height - 40)  # Sayfanın üst sol köşesinde başlıyor
    text_object.setFont("Helvetica", 10)

    # Metni satırlara ayırarak sayfaya ekliyoruz
    for line in text.splitlines():
        text_object.textLine(line)  # Her satırı ekliyoruz

    # Yazıyı sayfaya çiziyoruz ve dosyayı bitiriyoruz
    c.drawText(text_object)
    c.showPage()  # Yeni sayfa ekler
    c.save()  # PDF dosyasını kaydeder

    # Son olarak, tampondaki (buffer) veriyi belirtilen dosya yoluna kaydediyoruz
    with open(output_path, 'wb') as f:
        f.write(buffer.getvalue())


# Kullanım Örneği:
# create_pdf_from_text("Bu bir test makalesidir. İçerik burada yer alacak.", "output.pdf")

def extract_text_from_pdf(pdf_path):
    """
    Verilen PDF dosyasından metni çıkarır.
    """
    document = fitz.open(pdf_path)
    text = ""

    # PDF'deki her sayfayı döngüye alıyoruz
    for page_num in range(document.page_count):
        page = document.load_page(page_num)
        text += page.get_text()

    return text


# utils.py

import PyPDF2
import os
from django.conf import settings
from PIL import Image
from io import BytesIO


def extract_text_and_images_from_pdf(pdf_path):
    # PDF içeriğini çıkaran fonksiyon
    content = ""

    # PDF dosyasını aç
    with open(pdf_path, "rb") as file:
        reader = PyPDF2.PdfReader(file)

        # PDF sayfalarındaki metni çıkar
        for page in reader.pages:
            content += page.extract_text() or ""

    return content

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from PIL import Image
import os

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




import fitz  # PyMuPDF kütüphanesi

import os
from django.conf import settings
from collections import Counter
from .models import Article, MainSubtopic
