# 🤝 Jak współpracować przy projekcie YouTube to MP3 Converter

Dziękujemy za zainteresowanie współpracą! 🎉

## 📋 Jak zacząć?

### 1. Fork i Clone
```bash
# Fork repozytorium na GitHubie
# Następnie sklonuj swój fork:
git clone https://github.com/crahdlinuxservers-maker/YouTubeToMP3.git
cd YouTubeToMP3
```

### 2. Środowisko
```bash
# Utwórz wirtualne środowisko
python -m venv .venv

# Aktywuj (Windows)
.venv\Scripts\activate

# Zainstaluj zależności
pip install -r requirements.txt
```

### 3. Stwórz branch
```bash
git checkout -b feature/twoja-nowa-funkcja
```

### 4. Koduj!
- Pisz czytelny kod
- Dodawaj komentarze po polsku
- Stosuj konwencję nazewnictwa z projektu

### 5. Testuj
```bash
# Uruchom aplikację
python youtube_to_mp3.py

# Sprawdź czy wszystko działa
```

### 6. Commit i Push
```bash
git add .
git commit -m "✨ Dodano nową funkcję: opis"
git push origin feature/twoja-nowa-funkcja
```

### 7. Pull Request
- Otwórz Pull Request na GitHubie
- Opisz co zmieniłeś
- Poczekaj na review

---

## 📝 Standardy kodu

### Styl kodu
- **PEP 8** - podstawowe zasady Pythona
- **Komentarze PL** - wszystkie komentarze po polsku
- **Docstrings** - dla funkcji i klas
- **Logowanie** - używaj `logger.info()`, `logger.error()` etc.

### Przykład:
```python
def moja_funkcja(parametr: str) -> bool:
    """
    # KOMENTARZ PL: Opis funkcji po polsku
    # HASH_TAG: Tag do identyfikacji
    """
    logger.info(f"🔧 Rozpoczęto moja_funkcja: {parametr}")
    
    try:
        # Twoja logika
        result = True
        return result
    except Exception as e:
        logger.error(f"❌ Błąd w moja_funkcja: {str(e)}")
        return False
```

---

## 🐛 Zgłaszanie błędów

### Format Issue:
```markdown
**Opis błędu:**
Krótki opis co się dzieje

**Kroki do odtworzenia:**
1. Krok 1
2. Krok 2
3. ...

**Oczekiwane zachowanie:**
Co powinno się stać

**Rzeczywiste zachowanie:**
Co się dzieje

**Środowisko:**
- OS: Windows 10
- Python: 3.14
- Wersja: 2.0

**Logi/Screenshots:**
Załącz logi lub zrzuty ekranu
```

---

## ✨ Propozycje nowych funkcji

### Format Feature Request:
```markdown
**Funkcja:**
Nazwa funkcji

**Opis:**
Szczegółowy opis co ma robić

**Dlaczego:**
Dlaczego to jest potrzebne

**Przykład użycia:**
Jak użytkownik będzie z tego korzystał
```

---

## 🎯 Priorytety rozwoju

### Co jest mile widziane:
- ✅ Tłumaczenia (English, Deutsch, etc.)
- ✅ Obsługa innych platform (Vimeo, SoundCloud)
- ✅ Tryb wsadowy (batch processing)
- ✅ Harmonogram pobierania
- ✅ Integracja z cloud storage
- ✅ Testy jednostkowe
- ✅ Dokumentacja

### Co NIE jest mile widziane:
- ❌ Łamanie ToS YouTube
- ❌ Usuwanie watermarków
- ❌ Komercyjne wykorzystanie bez zgody
- ❌ Złośliwy kod
- ❌ Naruszanie praw autorskich

---

## 📞 Kontakt

**Autor:** Stanisław Kozioł  
**GitHub:** [crahdlinuxservers-maker](https://github.com/crahdlinuxservers-maker)

Pytania? Napisz:
- **[GitHub Issues](https://github.com/crahdlinuxservers-maker/YouTubeToMP3/issues)** - dla błędów i propozycji
- **Pull Requests** - dla kodu

---

**Dziękujemy za współpracę! ❤️**

