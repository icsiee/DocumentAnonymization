import fitz  # PyMuPDF

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from io import BytesIO


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
