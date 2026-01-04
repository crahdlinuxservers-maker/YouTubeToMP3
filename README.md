# 🎵 YouTube to MP3 Converter

**Profesjonalna aplikacja do konwersji YouTube na MP3 (320 kbps)**

## 📋 Autor
**Stanisław Kozioł**

---

## 🚀 Funkcje

✅ **Konwersja YouTube → MP3** (maksymalna jakość 320 kbps)  
✅ **Nowoczesny GUI** (CustomTkinter)  
✅ **Automatyczne pobieranie FFmpeg**  
✅ **Polski interfejs**  
✅ **Pasek postępu**  
✅ **Przenośny EXE** (bez instalacji)  
✅ **Bezpieczny kod** (bez wirusów)  

---

## 📦 Instalacja

### Opcja 1: Użyj gotowego EXE (ZALECANE)
1. Pobierz plik `YouTubeToMP3.exe` z folderu `dist`
2. Uruchom - gotowe! 🎉

### Opcja 2: Uruchom z kodu źródłowego
```bash
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
python -m PyInstaller --onefile --windowed --name=YouTubeToMP3 youtube_to_mp3.py
```

---

## 📖 Instrukcja użytkowania

1. **Uruchom aplikację**
2. **Wklej link YouTube** w pole tekstowe
3. **Kliknij "Sprawdź"** aby zobaczyć informacje o wideo
4. **Wybierz folder** (opcjonalnie) - domyślnie: `Pobrane\YouTube_MP3`
5. **Kliknij "KONWERTUJ"** i czekaj
6. **Gotowe!** Plik MP3 jest w folderze docelowym

---

## 🛠️ Technologie

- **Python 3.14**
- **CustomTkinter** - nowoczesny GUI
- **yt-dlp** - pobieranie z YouTube
- **FFmpeg** - konwersja audio
- **PyInstaller** - budowanie EXE

---

## ⚙️ Wymagania systemowe

- **Windows 7 / 8 / 10 / 11** (32-bit lub 64-bit)
- **Połączenie internetowe**
- **~50MB wolnego miejsca** (dla FFmpeg)

---

## 🐞 Rozwiązywanie problemów

### Antywirus blokuje EXE
**Rozwiązanie:** To normalne dla nowych EXE. Kliknij "Uruchom mimo to" lub dodaj do wyjątków.

### FFmpeg nie pobiera się
**Rozwiązanie:** Sprawdź połączenie internetowe. Kliknij przycisk "Zainstaluj FFmpeg" ręcznie.

### Błąd podczas konwersji
**Rozwiązanie:** Link może być nieprawidłowy lub wideo niedostępne. Spróbuj innego linku.

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
│
├── dist/                 # Folder z gotowym EXE
├── build/                # Folder tymczasowy (build)
├── ffmpeg/               # FFmpeg (pobierany automatycznie)
└── logs/                 # Logi aplikacji
```

---

## 📝 Changelog

### v1.0 (2026-01-04)
- ✅ Pierwsza wersja
- ✅ Konwersja YouTube → MP3 (320 kbps)
- ✅ Nowoczesny GUI
- ✅ Automatyczne pobieranie FFmpeg
- ✅ Polski interfejs
- ✅ Budowanie EXE

---


## 📜 Licencja

**Educational Project - 2026**

Projekt edukacyjny stworzony w celach nauki programowania.

---

## 📧 Kontakt

**Autor:** Stanisław Kozioł

---

**Made with ❤️ in Python**

