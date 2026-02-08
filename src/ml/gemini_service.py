from google import genai
import os
import re

class GeminiMusicStyler:
    def __init__(self):
        self.api_key = os.environ.get("GEMINI_API_KEY")
        self.client = None
        
        if self.api_key:
            try:
                # Client'ı başlat
                self.client = genai.Client(api_key=self.api_key)
            except Exception as e:
                print(f"Client Başlatma Hatası: {e}")

    def get_recommendation(self, mood: str, vibe_data: list) -> str:
        if not self.client:
            return "Tarkan - Yolla"

        # Vibe verisini metne dök
        vibe_desc = ", ".join([f"%{int(v['conf']*100)} {v['class']}" for v in vibe_data])
        
        prompt = f"""
        GÖREV: Verilen moda uygun SADECE 1 ADET şarkı öner.
        
        Mod: {mood}
        Detaylar: {vibe_desc}
        
        KURALLAR:
        1. SADECE "Sanatçı Adı - Şarkı Adı" formatında yaz.
        2. ASLA açıklama, yorum, madde işareti, sayı veya tırnak işareti kullanma.
        3. Birden fazla şarkı önerme.
        4. Fizy'de bulunabilecek popüler bir şarkı olsun.
        
        Örnek Çıktı:
        Müslüm Gürses - Nilüfer
        """
        
        try:
            # En güvenli ve hızlı model: gemini-1.5-flash
            response = self.client.models.generate_content(
                model="gemini-flash-latest",
                contents=prompt
            )
            return self._clean_response(response.text)

        except Exception as e:
            print(f"Gemini Hatası: {str(e)}")
            return "Tarkan - Yolla"

    def _clean_response(self, text):
        """Cevabı temizler ve ekstra boşlukları yok eder"""
        if not text: return "Tarkan - Yolla"
        
        # 1. İlk satırı al
        first_line = text.strip().split('\n')[0]
        
        # 2. İşaretleri temizle
        clean = first_line.replace('*', '').replace('"', '').replace("'", "")
        clean = re.sub(r'^\d+\.\s*', '', clean)
        
        # 3. Tireyi boşluğa çevir
        clean = clean.replace('-', ' ')

        # 🔥 KRİTİK NOKTA: Çift/Üçlü boşlukları TEK boşluğa indir
        # "Enya   Orinoco" -> "Enya Orinoco" olur.
        clean = re.sub(r'\s+', ' ', clean)
        
        return clean.strip()