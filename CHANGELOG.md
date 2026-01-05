# 📝 Changelog

Wszystkie istotne zmiany w projekcie YouTube to MP3 Converter będą dokumentowane w tym pliku.

Format bazuje na [Keep a Changelog](https://keepachangelog.com/pl/1.0.0/),
a projekt stosuje [Semantic Versioning](https://semver.org/lang/pl/).

## [2.0.0] - 2026-01-05

### ✨ Dodano
- **Pobieranie playlist** - selektor wideo z playlisty YouTube
- **Historia pobierań** - baza danych SQLite ze wszystkimi konwersjami
- **Automatyczne tagowanie ID3** - metadata i okładki dla plików MP3
- **Wybór jakości audio** - 128, 192, 256, 320 kbps
- **Wybór formatu** - MP3, M4A, WAV, OPUS
- **Panel informacji** - miniaturka, tytuł, kanał, czas trwania
- **Zaawansowany pasek postępu** - prędkość, ETA, dane techniczne
- **Przycisk "Wyczyść wyszukiwanie"** - reset formularza
- **Przyciski "Zaznacz/Odznacz wszystkie"** - dla playlist
- **Menu "Historia"** - wyświetlanie historii pobierań
- **Menu "Wyczyść historię"** - czyszczenie bazy danych
- **Menu "Informacje"** - statystyki pobierań

### 🔧 Zmieniono
- **Stały rozmiar okna** - 700x700px (poprzednio: dynamiczny)
- **UI/UX** - elegantszy design, lepsze rozmieszczenie elementów
- **Domyślny stan playlist** - wszystkie wideo odznaczone (poprzednio: zaznaczone)
- **Pasek postępu** - bardziej szczegółowe informacje
- **Panel informacji** - wizualnie ulepszony z obramowaniem

### 🐛 Naprawiono
- Nakładanie się wideo w selectorze playlist przy przewijaniu
- Błąd resetu miniaturek przy klikaniu "Sprawdź"
- Problem z przewijaniem stron w playlistach
- Brak widoczności przycisków przy różnych rozmiarach okna
- Błąd `TclError: image "pyimage1" doesn't exist`

### 📚 Dokumentacja
- Zaktualizowany **README.md** z nowymi funkcjami
- Dodano **LICENSE** (MIT)
- Dodano **CONTRIBUTING.md** - instrukcje dla współpracowników
- Dodano **QUICKSTART_GITHUB.md** - szybki start
- Dodano **.gitignore** - ignorowanie plików tymczasowych
- Dodano **.gitattributes** - zarządzanie końcami linii
- Dodano szablony **Issue** i **Pull Request** dla GitHub

---

## [1.0.0] - 2026-01-04

### ✨ Dodano
- **Podstawowa konwersja** YouTube → MP3 (320 kbps)
- **Nowoczesny GUI** oparty na CustomTkinter
- **Automatyczne pobieranie FFmpeg**
- **Polski interfejs**
- **Pasek postępu** z podstawowymi informacjami
- **Wybór folderu docelowego**
- **Logowanie** do plików i konsoli
- **Budowanie EXE** przez PyInstaller

### 🎯 Pierwsze wydanie
Pierwsza wersja aplikacji YouTube to MP3 Converter z podstawowymi funkcjami konwersji.

---

## [Unreleased]

### 🚧 W planach
- Tłumaczenia (English, Deutsch, Español)
- Obsługa innych platform (Vimeo, SoundCloud)
- Tryb wsadowy (batch processing)
- Harmonogram pobierania
- Integracja z cloud storage
- Testy jednostkowe
- Ciemny/Jasny motyw

---

**Legenda:**
- ✨ Dodano - nowe funkcje
- 🔧 Zmieniono - zmiany w istniejących funkcjach
- 🐛 Naprawiono - poprawki błędów
- ❌ Usunięto - usunięte funkcje
- 🔒 Bezpieczeństwo - poprawki bezpieczeństwa
- 📚 Dokumentacja - zmiany w dokumentacji

