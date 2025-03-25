from cryptography.fernet import Fernet

# Fernet anahtarını oluştur
key = Fernet.generate_key()

# Anahtarı bir dosyaya yaz veya yazdır
print(key.decode())  # Anahtarı yazdır
