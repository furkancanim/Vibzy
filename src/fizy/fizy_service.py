import requests
import urllib.parse

class FizyService:
    BASE_URL = "https://listen.fizy.com/hafifmuzik/mobile/fastsearch/v2/autocompleteall"
    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Referer": "https://fizy.com/",
        "X-Requested-With": "XMLHttpRequest"
    }

    def search_song(self, query: str) -> dict:
        """Şarkıyı arar ve bulamazsa sanatçı adıyla tekrar dener."""
        if not query: return {"found": False}

        # 1. Tam sorguyu dene (Örn: Teoman İstanbul'da Sonbahar)
        if result := self._fetch(query):
            return result
        
        # 2. Bulamazsa sadece ilk kelimeyi (Sanatçıyı) dene (Örn: Teoman)
        first_word = query.split()[0]
        if first_word != query:
            return self._fetch(first_word) or {"found": False}
            
        return {"found": False}

    def _fetch(self, query):
        try:
            # URL Parametrelerini Hazırla
            # API isteği için boşlukları %20 yapıyoruz (quote)
            encoded_query = urllib.parse.quote(query)
            url = f"{self.BASE_URL}?q={encoded_query}&withlimit=50&onlystreamable=false"
            
            resp = requests.get(url, headers=self.HEADERS, timeout=5)
            if resp.status_code != 200: return None

            # JSON yanıtını işle (result kutusunu aç)
            data = resp.json()
            data = data.get("result", data)

            # Öncelik sırasına göre kategorileri tara
            for category in ["bestResult", "songs", "artists", "albums", "videos"]:
                for item in data.get(category, []):
                    
                    # Verileri çek
                    title = item.get("label")
                    # Artist bazen 'extra' içinde, bazen gelmez
                    artist = item.get("extra", {}).get("artistname") or title 

                    # Resmi al ve boyutunu ayarla
                    img_raw = item.get("imagePath", "")
                    image = img_raw.replace("[size]", "300x300") if img_raw else "https://fizy.com/assets/images/logo.png"

                    # 🔥 ÇALIŞAN FİNAL LİNK YAPISI 🔥
                    # Link: https://listen.fizy.com/search?query=Artist+Title
                    # URL içinde boşlukları '+' yapmak için quote_plus kullanıyoruz.
                    search_slug = urllib.parse.quote_plus(f"{artist} {title}")
                    link = f"https://listen.fizy.com/search?query={search_slug}"

                    return {
                        "found": True,
                        "title": title,
                        "artist": artist,
                        "image": image,
                        "link": link
                    }

        except Exception as e:
            print(f"Fizy Servis Hatası: {e}")
            
        return None