#
import os
from dotenv import load_dotenv
from google import genai

load_dotenv()
api_key = os.environ.get("GEMINI_API_KEY")

print("📡 Google'a Bağlanılıyor...")

try:
    # İstemciyi başlat
    client = genai.Client(api_key=api_key)
    
    # Modelleri listele ve sadece isimlerini yazdır
    print("\n--- KULLANILABİLİR MODELLERİN ---")
    for m in client.models.list():
        print(f"Model: {m.name}")
        
    print("\n✅ Listeleme bitti.")
    
except Exception as e:
    print(f"❌ HATA: {e}")