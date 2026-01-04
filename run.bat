@echo off
REM ============================================================================
REM  YouTube to MP3 Converter - Quick Run
REM  Autor: Stanisław Kozioł
REM ============================================================================

echo.
echo ============================================================================
echo  YOUTUBE TO MP3 CONVERTER
echo ============================================================================
echo.

REM Sprawdź venv
if not exist "venv\Scripts\activate.bat" (
    echo [ERROR] Wirtualne środowisko nie istnieje!
    echo Uruchom najpierw: setup.bat
    pause
    exit /b 1
)

REM Aktywuj i uruchom
call venv\Scripts\activate.bat
python youtube_to_mp3.py

pause

