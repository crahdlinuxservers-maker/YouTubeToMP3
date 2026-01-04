@echo off
REM ============================================================================
REM  YouTube to MP3 Converter - Quick Setup
REM  Autor: Stanisław Kozioł
REM ============================================================================

echo.
echo ============================================================================
echo  YOUTUBE TO MP3 CONVERTER - INSTALACJA
echo ============================================================================
echo.

REM Sprawdź Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python nie jest zainstalowany!
    echo Pobierz Python z: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo [OK] Python wykryty
echo.

REM Stwórz venv
echo [1/3] Tworzenie wirtualnego środowiska...
python -m venv venv
if errorlevel 1 (
    echo [ERROR] Nie udało się stworzyć venv
    pause
    exit /b 1
)

echo [OK] Wirtualne środowisko stworzone
echo.

REM Aktywuj venv
echo [2/3] Aktywacja środowiska...
call venv\Scripts\activate.bat

REM Instaluj zależności
echo [3/3] Instalacja bibliotek...
pip install -r requirements.txt --upgrade --quiet

if errorlevel 1 (
    echo [ERROR] Błąd instalacji bibliotek
    pause
    exit /b 1
)

echo.
echo ============================================================================
echo  INSTALACJA ZAKOŃCZONA!
echo ============================================================================
echo.
echo Aby uruchomić program:
echo   1. venv\Scripts\activate.bat
echo   2. python youtube_to_mp3.py
echo.
echo Lub zbuduj EXE:
echo   python build_exe.py
echo.
echo ============================================================================
pause

