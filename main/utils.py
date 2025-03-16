import fitz  # PyMuPDF

def pdf_to_text(pdf_path):
    doc = fitz.open(pdf_path)  # PDF dosyasını aç
    text = ""
    for page_num in range(doc.page_count):  # Her sayfayı gez
        page = doc.load_page(page_num)  # Sayfayı yükle
        text += page.get_text()  # Sayfadaki metni al
    return text
