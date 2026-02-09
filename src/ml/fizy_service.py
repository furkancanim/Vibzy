# src/ml/fizy_service.py
import urllib.parse
import urllib.request
import json

class FizyService:
    AUTOCOMPLETE_URL = "https://listen.fizy.com/hafifmuzik/mobile/fastsearch/v2/autocompleteall"

    PLAY_URL_TEMPLATE = (
        "https://listen.fizy.com/album/--/fzy/fzy/vfitmzyxnzm5odm3odmwng/--/sarkilar/fzy/{song_id}/simdi-cal"
    )

    DEFAULT_IMAGE = "https://play-lh.googleusercontent.com/ALi2r3mZcU0MdhzBGoboHUrjg1rfGTLAYytiPZXIOB5vQIG1JC-S1K1Lt_WseGtYa4U"

    def search_song(self, query: str) -> dict:
        q = (query or "").strip()
        if not q:
            return {"found": False}

        # 1) İlk deneme: tam sorgu
        song = self._first_song(q)

        # 2) Bulunamazsa: sadece şarkı adıyla dene ("Artist - Song" veya "Artist Song" -> "Song")
        if not song:
            title_only = self._title_only(q)
            if title_only and title_only != q:
                song = self._first_song(title_only)

        # 3) Hâlâ yoksa: UI "müzik bulunamadı" demesin diye arama linkine düş
        if not song:
            return {
                "found": True,
                "title": q,
                "artist": "Fizy'de Ara",
                "image": self.DEFAULT_IMAGE,
                "link": f"https://listen.fizy.com/search?query={urllib.parse.quote_plus(q)}",
            }

        song_id = str(song.get("id") or "").strip()
        if not song_id:
            return {"found": False}

        return {
            "found": True,
            "title": (song.get("label") or q).strip(),
            "artist": ((song.get("extra") or {}).get("artistname") or "Fizy").strip(),
            "image": (song.get("imagePath") or "").replace("[size]", "400x400") or self.DEFAULT_IMAGE,
            "link": self.PLAY_URL_TEMPLATE.format(song_id=song_id),
        }

    # ---- helpers (kısa) ----
    def _first_song(self, q: str):
        params = {"withlimit": "100", "onlystreamable": "false", "q": self._clean(q)}
        url = self.AUTOCOMPLETE_URL + "?" + urllib.parse.urlencode(params, quote_via=urllib.parse.quote)
        req = urllib.request.Request(url, headers={"Accept": "application/json", "User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=8) as resp:
            data = json.loads(resp.read().decode("utf-8", errors="replace"))
        songs = (data.get("result") or {}).get("songs") or []
        return songs[0] if songs else None

    def _title_only(self, q: str) -> str:
        q = self._clean(q)
        if " - " in q:  # Artist - Song
            return q.split(" - ", 1)[1].strip()
        if "-" in q:    # Artist-Song
            return q.split("-", 1)[1].strip()
        p = q.split()   # Artist Song Name -> Song Name
        return " ".join(p[1:]).strip() if len(p) >= 3 else q

    def _clean(self, s: str) -> str:
        s = (s or "").strip()
        for ch in ['"', "'", "“", "”", "‘", "’"]:
            s = s.replace(ch, "")
        return " ".join(s.split())
