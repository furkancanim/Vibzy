from google import genai
import os

class GeminiMusicStyler:
    def __init__(self):
        self.api_key = os.environ.get("GEMINI_API_KEY")
        self.client = None
        if self.api_key:
            
            self.client = genai.Client(api_key=self.api_key)

    def get_recommendation(self, mood, vibe_mix):
        if not self.client:
            return "API anahtarı eksik"

        vibe_desc = ", ".join([f"%{int(v['conf']*100)} {v['class']}" for v in vibe_mix])
        
        prompt = f"""
        Sen bir DJ'sin.
        Atmosfer: {mood}
        Detaylar: {vibe_desc}
        
        Bu moda uygun 3 şarkı öner (Sanatçı - Şarkı). 
        Her şarkı için nedenini 1 kısa cümleyle açıkla.
        Sadece Markdown listesi olarak cevap ver.
        """
        
        try:
          
            response = self.client.models.generate_content(
                model="gemini-flash-latest", 
                contents=prompt
            )
            return response.text
        except Exception as e:
            # hata
            print(f" Gemini Hatası: {str(e)}")
            return f"Öneri alınamadı: {str(e)}"