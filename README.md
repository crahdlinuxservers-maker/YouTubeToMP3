# 🎵 YouTube to MP3 Converter

**Profesjonalna aplikacja do konwersji YouTube na MP3 z zaawansowanymi funkcjami**

![Version](https://img.shields.io/badge/version-2.0-blue)
![Python](https://img.shields.io/badge/python-3.14-green)
![License](https://img.shields.io/badge/license-MIT-orange)

## 📋 Autor
**Stanisław Kozioł**

---

## 🚀 Nowe funkcje w wersji 2.0

✅ **Konwersja YouTube → MP3** (maksymalna jakość 320 kbps)  
✅ **Pobieranie playlist** - wybierz konkretne wideo z playlisty  
✅ **Historia pobierań** - śledź wszystkie konwersje  
✅ **Automatyczne tagowanie ID3** - tytuł, artysta, okładka  
✅ **Wybór jakości audio** - 128, 192, 256, 320 kbps  
✅ **Wybór formatu** - MP3, M4A, WAV, OPUS  
✅ **Nowoczesny GUI** z CustomTkinter  
✅ **Automatyczne pobieranie FFmpeg**  
✅ **Zaawansowany pasek postępu** z informacjami technicznymi  
✅ **Panel informacji** z miniaturką, tytułem, kanałem i czasem trwania  
✅ **Stały rozmiar okna** (700x700px) - responsywny interfejs  
✅ **Polski interfejs**  
✅ **Przenośny EXE** (bez instalacji)  

---

## 📦 Instalacja

### Opcja 1: Użyj gotowego EXE (ZALECANE)
1. Pobierz plik `YouTubeToMP3.exe` z [Releases](https://github.com/crahdlinuxservers-maker/YouTubeToMP3/releases)
2. Uruchom - gotowe! 🎉

### Opcja 2: Uruchom z kodu źródłowego
```bash
# Sklonuj repozytorium
git clone https://github.com/crahdlinuxservers-maker/YouTubeToMP3.git
cd YouTubeToMP3

# Zainstaluj wymagane biblioteki
pip install -r requirements.txt

# Uruchom aplikację
python youtube_to_mp3.py
```

---

## 🔨 Budowanie EXE

```bash
# Automatyczny build
python build_exe.py

# Lub ręcznie z PyInstaller
python -m PyInstaller --onefile --windowed --name=YouTubeToMP3 --icon=logo.png youtube_to_mp3.py
```

---

## 📖 Instrukcja użytkowania

### Pojedyncze wideo:
1. **Uruchom aplikację**
2. **Wklej link YouTube** w pole tekstowe
3. **Kliknij "Sprawdź"** aby zobaczyć informacje o wideo
4. **Wybierz jakość audio** (domyślnie 320 kbps)
5. **Wybierz format** (domyślnie MP3)
6. **Wybierz folder** (opcjonalnie) - domyślnie: `Pobrane\YouTube_MP3`
7. **Kliknij "KONWERTUJ"** i czekaj
8. **Gotowe!** Plik jest w folderze docelowym

### Playlista YouTube:
1. **Wklej link do playlisty**
2. **Zaznacz checkbox "Playlista"**
3. **Kliknij "Sprawdź"**
4. **Wybierz wideo** które chcesz pobrać (domyślnie wszystkie są odznaczone)
5. Użyj przycisków:
   - **"Zaznacz wszystkie"** - zaznacz wszystkie wideo
   - **"Odznacz wszystkie"** - wyczyść zaznaczenie
   - Przewijaj strony aby zobaczyć wszystkie wideo
6. **Kliknij "Pobierz zaznaczone"**
7. Program pobierze i skonwertuje wszystkie wybrane wideo

### Historia pobierań:
- **Menu → Historia** - wyświetla wszystkie pobrane pliki
- **Menu → Wyczyść historię** - usuwa historię (nie usuwa plików)
- **Menu → Informacje** - statystyki pobierań

---

## 🛠️ Technologie

- **Python 3.14**
- **CustomTkinter** - nowoczesny GUI
- **yt-dlp** - pobieranie z YouTube
- **FFmpeg** - konwersja audio
- **Mutagen** - tagowanie ID3
- **Pillow** - obsługa miniaturek
- **SQLite** - historia pobierań
- **PyInstaller** - budowanie EXE

---

## ⚙️ Wymagania systemowe

- **Windows 7 / 8 / 10 / 11** (32-bit lub 64-bit)
- **Połączenie internetowe**
- **~50MB wolnego miejsca** (dla FFmpeg)
- **Procesor:** dowolny (zalecane 2+ rdzenie)
- **RAM:** minimum 512MB

---

## 🐞 Rozwiązywanie problemów

### Antywirus blokuje EXE
**Rozwiązanie:** To normalne dla nowych EXE. Kliknij "Uruchom mimo to" lub dodaj do wyjątków.

### FFmpeg nie pobiera się
**Rozwiązanie:** Sprawdź połączenie internetowe. Kliknij przycisk "Zainstaluj FFmpeg" ręcznie.

### Błąd podczas konwersji
**Rozwiązanie:** Link może być nieprawidłowy lub wideo niedostępne. Spróbuj innego linku.

### Nie widać przycisków na dole
**Rozwiązanie:** Upewnij się że okno ma rozmiar 700x700px. Program ma stały rozmiar.

### Playlista nie pokazuje wszystkich wideo
**Rozwiązanie:** Użyj przycisków "Następna/Poprzednia" aby przewijać strony (50 wideo na stronę).

---

## 📂 Struktura projektu

```
YouTubeToMP3/
│
├── youtube_to_mp3.py      # Główny program
├── build_exe.py           # Skrypt budowania EXE
├── requirements.txt       # Wymagane biblioteki
├── version_info.txt       # Metadata dla EXE
├── logo.png              # Ikona aplikacji
├── README.md             # Ten plik
├── LICENSE               # Licencja MIT
├── .gitignore            # Pliki ignorowane przez Git
│
├── dist/                 # Folder z gotowym EXE (ignorowany)
├── build/                # Folder tymczasowy (ignorowany)
├── ffmpeg/               # FFmpeg (pobierany automatycznie, ignorowany)
├── logs/                 # Logi aplikacji (ignorowany)
└── __pycache__/          # Cache Pythona (ignorowany)
```

---

## 📝 Changelog

### v2.0 (2026-01-05)
- ✅ **Pobieranie playlist** - selektor wideo z playlisty
- ✅ **Historia pobierań** - SQLite database
- ✅ **Automatyczne tagowanie ID3** - metadata + okładki
- ✅ **Wybór jakości audio** - 128/192/256/320 kbps
- ✅ **Wybór formatu** - MP3/M4A/WAV/OPUS
- ✅ **Panel informacji** - miniaturka + metadata
- ✅ **Zaawansowany pasek postępu** - prędkość, ETA, dane techniczne
- ✅ **Przycisk "Wyczyść wyszukiwanie"** - reset formularza
- ✅ **Stały rozmiar okna** - 700x700px
- ✅ **Ulepszony UX/UI** - elegancki design

### v1.0 (2026-01-04)
- ✅ Pierwsza wersja
- ✅ Konwersja YouTube → MP3 (320 kbps)
- ✅ Nowoczesny GUI
- ✅ Automatyczne pobieranie FFmpeg
- ✅ Polski interfejs
- ✅ Budowanie EXE

---

## 🤝 Współpraca

Chcesz pomóc? Wspaniale! 

1. **Fork** projektu
2. Stwórz **branch** (`git checkout -b feature/NowaFunkcja`)
3. **Commit** zmian (`git commit -m 'Dodano nową funkcję'`)
4. **Push** do brancha (`git push origin feature/NowaFunkcja`)
5. Otwórz **Pull Request**

---

## 📜 Licencja

MIT License - szczegóły w pliku [LICENSE](LICENSE)

---

## 📧 Kontakt

**Autor:** Stanisław Kozioł  
**GitHub:** [crahdlinuxservers-maker](https://github.com/crahdlinuxservers-maker/YouTubeToMP3)

---

## ⭐ Podziękowania

- **yt-dlp** - za świetną bibliotekę do pobierania z YouTube
- **CustomTkinter** - za nowoczesny framework GUI
- **FFmpeg** - za potężne narzędzie do konwersji

---

**Made with ❤️ in Python**

