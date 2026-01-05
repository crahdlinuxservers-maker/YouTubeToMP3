# 🚀 Deployment & Release Guide

## 📦 Tworzenie nowego wydania

### 1. Przygotowanie
```bash
# Upewnij się że wszystko działa
python youtube_to_mp3.py

# Sprawdź testy (jeśli są)
pytest tests/
```

### 2. Aktualizacja wersji
- Zmień numer wersji w `version_info.txt`
- Zaktualizuj `CHANGELOG.md`
- Zaktualizuj badge wersji w `README.md`

### 3. Budowanie EXE
```bash
# Zbuduj aplikację
python build_exe.py

# Plik będzie w: dist/YouTubeToMP3.exe
```

### 4. Testowanie EXE
- Uruchom `dist/YouTubeToMP3.exe`
- Przetestuj wszystkie funkcje:
  - Pojedyncze wideo
  - Playlista
  - Różne formaty
  - Historia
  - Statystyki

### 5. Commit i Push
```bash
git add .
git commit -m "🚀 Release v2.0 - Pełna funkcjonalność"
git push origin main
```

### 6. Tworzenie Release na GitHub
1. Przejdź do: https://github.com/crahdlinuxservers-maker/YouTubeToMP3/releases
2. Kliknij **"Draft a new release"**
3. Tag version: `v2.0`
4. Release title: `🎵 YouTube to MP3 Converter v2.0`
5. Opisz zmiany (skopiuj z CHANGELOG.md)
6. Załącz pliki:
   - `YouTubeToMP3.exe` (z folderu dist/)
7. Kliknij **"Publish release"**

---

## 📋 Checklist przed Release

- [ ] Wszystkie funkcje działają
- [ ] Zaktualizowano CHANGELOG.md
- [ ] Zaktualizowano numer wersji
- [ ] Zbudowano EXE
- [ ] Przetestowano EXE na czystym systemie
- [ ] Zaktualizowano dokumentację
- [ ] Commit i push do GitHub
- [ ] Utworzono Release z załączonym EXE

---

## 🔄 Continuous Deployment (opcjonalne)

### GitHub Actions
Możesz zautomatyzować budowanie EXE poprzez GitHub Actions.

Stwórz plik `.github/workflows/build.yml`:

```yaml
name: Build EXE

on:
  push:
    tags:
      - 'v*'

jobs:
  build:
    runs-on: windows-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.14'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
    
    - name: Build EXE
      run: python build_exe.py
    
    - name: Upload Release Asset
      uses: actions/upload-artifact@v3
      with:
        name: YouTubeToMP3.exe
        path: dist/YouTubeToMP3.exe
```

---

## 📧 Komunikacja

Po wydaniu nowej wersji:
1. Zaktualizuj README.md z nowym linkiem
2. Poinformuj użytkowników w Issues
3. Dodaj informację w Discussions (jeśli włączone)

---

**Autor:** Stanisław Kozioł  
**GitHub:** https://github.com/crahdlinuxservers-maker/YouTubeToMP3

