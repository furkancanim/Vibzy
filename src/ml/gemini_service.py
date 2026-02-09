from google import genai
import os
import re

class GeminiMusicStyler:
    def __init__(self):
        self.api_key = os.environ.get("GEMINI_API_KEY")
        self.client = None
        
        if self.api_key:
            try:
                # client
                self.client = genai.Client(api_key=self.api_key)
            except Exception as e:
                print(f"Client Başlatma Hatası: {e}")

    def get_recommendation(self, mood: str, vibe_data: list) -> str:
        if not self.client:
            return "Tarkan - Yolla"

        # vibe -> metin
        vibe_desc = ", ".join([f"%{int(v['conf']*100)} {v['class']}" for v in vibe_data])
        
        prompt = f"""
        GÖREV: Verilen moda uygun SADECE 1 ADET şarkı öner. Gerçekten var olan bir şarkı olmak zorunda. Mood sadece resim hakkında bir fikir vermesi içindir. Şarkıları özgürce seç.

        
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
            # model secimi
            response = self.client.models.generate_content(
                model="gemini-flash-latest",
                contents=prompt
            )
            return self._clean_response(response.text)

        except Exception as e:
            print(f"Gemini Hatası: {str(e)}")
            return "Tarkan - Yolla"

    def _clean_response(self, text):
        
        if not text: return "Tarkan - Yolla"
        
        # ilk satırı al
        first_line = text.strip().split('\n')[0]
        
        # isaretlerin temizligi bosluk duzltme

        clean = first_line.replace('*', '').replace('"', '').replace("'", "")
        clean = re.sub(r'^\d+\.\s*', '', clean)
        
       
        clean = clean.replace('-', ' ')

        # bosluk azaltma
        clean = re.sub(r'\s+', ' ', clean)
        
        return clean.strip()