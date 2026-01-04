"""
╔════════════════════════════════════════════════════════════════════════════╗
║                    BUILDER - YouTube to MP3 Converter EXE                  ║
║                                                                             ║
║  Autor: Stanisław Kozioł                                                   ║
║  Opis: Skrypt do budowania profesjonalnego EXE dla Windows                 ║
║                                                                             ║
║  # HASH_EXE_BUILDER: Tworzenie przenośnego EXE                             ║
║  # KOMENTARZ PL: Bez zależności - jednoplikowy program                     ║
╚════════════════════════════════════════════════════════════════════════════╝
"""

import os
import sys
import subprocess
from pathlib import Path

# ═══════════════════════════════════════════════════════════════════════════
# KONFIGURACJA
# ═══════════════════════════════════════════════════════════════════════════

PROJECT_DIR = Path(__file__).parent
MAIN_FILE = PROJECT_DIR / "youtube_to_mp3.py"
OUTPUT_DIR = PROJECT_DIR / "dist"
BUILD_DIR = PROJECT_DIR / "build"
SPEC_DIR = PROJECT_DIR

# HASH_PYINSTALLER_CONFIG: Konfiguracja PyInstallera
PYINSTALLER_ARGS = [
    # Główny plik
    str(MAIN_FILE),

    # Output
    f"--distpath={OUTPUT_DIR}",
    f"--buildpath={BUILD_DIR}",
    f"--specpath={SPEC_DIR}",

    # Tryb jednoplikowy (bez konsoli)
    "--onefile",
    "--noconsole",

    # Optymalizacja
    "--optimize=2",
    "--strip",

    # Ikona (opcjonalnie)
    f'--icon={PROJECT_DIR / "logo.png"}' if (PROJECT_DIR / "logo.png").exists() else "",

    # Nazwa
    '--name=YouTubeToMP3',

    # Metadata
    '--version-file=' + str(PROJECT_DIR / "version.txt") if (PROJECT_DIR / "version.txt").exists() else "",

    # Hidden imports
    '--hidden-import=customtkinter',
    '--hidden-import=yt_dlp',
    '--hidden-import=PIL',

    # Dodatkowe pliki
    '--collect-all=customtkinter',
    '--collect-all=yt_dlp',
]

# Filtruj puste stringi
PYINSTALLER_ARGS = [arg for arg in PYINSTALLER_ARGS if arg]

def print_header():
    """Wyświetl nagłówek"""
    print("\n" + "═" * 80)
    print("🎵 YOUTUBE TO MP3 CONVERTER - EXE BUILDER")
    print("═" * 80)
    print(f"📁 Projekt: {PROJECT_DIR}")
    print(f"📄 Plik główny: {MAIN_FILE}")
    print(f"📦 Output: {OUTPUT_DIR}")
    print("═" * 80 + "\n")

def clean_build():
    """Wyczyść poprzednie buildy"""
    print("🧹 Czyszczenie poprzednich buildów...")
    for directory in [BUILD_DIR, OUTPUT_DIR, SPEC_DIR]:
        if directory.exists() and directory != SPEC_DIR:
            import shutil
            try:
                shutil.rmtree(directory)
                print(f"   ✅ Usunięto: {directory}")
            except Exception as e:
                print(f"   ⚠️  Błąd: {e}")

def build_exe():
    """Buduj EXE"""
    print("🔨 Budowanie EXE...\n")

    cmd = ["pyinstaller"] + PYINSTALLER_ARGS

    print(f"Polecenie: {' '.join(cmd)}\n")

    try:
        result = subprocess.run(cmd, cwd=PROJECT_DIR)
        return result.returncode == 0
    except Exception as e:
        print(f"❌ Błąd: {e}")
        return False

def create_launcher():
    """Stwórz batch launcher"""
    launcher_path = OUTPUT_DIR / "YouTubeToMP3.bat"

    launcher_content = """@echo off
REM YouTube to MP3 Converter Launcher
REM Autor: Stanisław Kozioł

setlocal enabledelayedexpansion

REM Zmień na folder aplikacji
cd /d "%~dp0"

REM Uruchom EXE
start YouTubeToMP3.exe

REM Zamknij batch
exit /b
"""

    with open(launcher_path, 'w', encoding='utf-8') as f:
        f.write(launcher_content)

    print(f"✅ Launcher: {launcher_path}")

def create_readme():
    """Stwórz README"""
    readme_path = OUTPUT_DIR / "README.txt"

    readme_content = """╔════════════════════════════════════════════════════════════════════════════╗
║                   YOUTUBE TO MP3 CONVERTER                                  ║
║                                                                              ║
║  Autor: Stanisław Kozioł                                                    ║
║  Wersja: 1.0                                                                ║
║                                                                              ║
║  Profesjonalna aplikacja do konwersji YouTube → MP3 (320 kbps)              ║
╚════════════════════════════════════════════════════════════════════════════╝

┌─────────────────────────────────────────────────────────────────────────────┐
│ JAK UŻYWAĆ                                                                  │
└─────────────────────────────────────────────────────────────────────────────┘

1. Uruchom: YouTubeToMP3.exe
2. Wklej link YouTube
3. Kliknij "Sprawdź" aby zobaczyć informacje
4. Kliknij "KONWERTUJ" aby pobrać plik
5. Poczekaj na zakończenie
6. Plik pojawi się w folderze "Pobrane\YouTube_MP3"

┌─────────────────────────────────────────────────────────────────────────────┐
│ WYMAGANIA                                                                   │
└─────────────────────────────────────────────────────────────────────────────┘

• Windows 7 lub nowszy (32-bit / 64-bit)
• Połączenie internetowe
• ~50MB wolnego miejsca (dla FFmpeg)

┌─────────────────────────────────────────────────────────────────────────────┐
│ CHARAKTERYSTYKA                                                             │
└─────────────────────────────────────────────────────────────────────────────┘

✅ Przenośny (nie wymaga instalacji)
✅ Jednoplikowy EXE
✅ Bez antywirusa (czysty kod)
✅ Polski interfejs
✅ Automatyczne pobieranie FFmpeg
✅ Maksymalna jakość 320 kbps MP3
✅ Nowoczesne GUI (CustomTkinter)

┌─────────────────────────────────────────────────────────────────────────────┐
│ PROBLEMY I ROZWIĄZANIA                                                      │
└─────────────────────────────────────────────────────────────────────────────┘

P: Antywirus blokuje aplikację
O: To normalne - EXE ze sobą nie ma, antywirus skanuje. Kliknij "Uruchom mimo to"

P: FFmpeg nie pobiera się
O: Upewnij się że masz połączenie internetowe. Kliknij "Zainstaluj FFmpeg"

P: Brak dźwięku w konwertowanym pliku
O: Link może być niedostępny - spróbuj inny

┌─────────────────────────────────────────────────────────────────────────────┐
│ NOTES TECHNICZNE                                                            │
└─────────────────────────────────────────────────────────────────────────────┘

• Autor: Stanisław Kozioł
• Framework: Python + CustomTkinter
• Konwerter: yt-dlp + FFmpeg
• Kodowanie: UTF-8
• Licencja: Edukacyjna (Learn Project)

═════════════════════════════════════════════════════════════════════════════

Miłego konwertowania! 🎵
"""

    with open(readme_path, 'w', encoding='utf-8') as f:
        f.write(readme_content)

    print(f"✅ README: {readme_path}")

def main():
    """Główna funkcja"""
    print_header()

    # Sprawdź czy plik istnieje
    if not MAIN_FILE.exists():
        print(f"❌ Błąd: Nie znaleziono {MAIN_FILE}")
        sys.exit(1)

    # Wyczyść
    clean_build()

    # Buduj
    success = build_exe()

    if not success:
        print("\n❌ Błąd budowania EXE")
        sys.exit(1)

    print("\n✅ EXE zbudowany pomyślnie!\n")

    # Stwórz dodatkowe pliki
    create_launcher()
    create_readme()

    # Podsumowanie
    print("\n" + "═" * 80)
    print("✅ BUDOWANIE ZAKOŃCZONE")
    print("═" * 80)
    print(f"📦 Plik: {OUTPUT_DIR / 'YouTubeToMP3.exe'}")
    print(f"📂 Folder: {OUTPUT_DIR}")
    print("\n🎉 Aplikacja jest gotowa do użytku!")
    print("═" * 80 + "\n")

if __name__ == "__main__":
    main()

