#!/bin/bash

# YouTube to MP3 Converter - Linux Installation Script
# Author: Stanisław Kozioł
# GitHub: https://github.com/crahdlinuxservers-maker/YouTubeToMP3

echo "╔════════════════════════════════════════════════════════╗"
echo "║     YouTube to MP3 Converter - Linux Setup            ║"
echo "║     Author: Stanisław Kozioł                          ║"
echo "╚════════════════════════════════════════════════════════╝"
echo ""

# Sprawdź czy Python3 jest zainstalowany
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 nie jest zainstalowany!"
    echo "Zainstaluj Python3:"
    echo "  Ubuntu/Debian: sudo apt install python3 python3-pip python3-venv"
    echo "  Fedora/RHEL: sudo dnf install python3 python3-pip"
    echo "  Arch: sudo pacman -S python python-pip"
    exit 1
fi

echo "✅ Python3 znaleziony: $(python3 --version)"

# Sprawdź ffmpeg
if ! command -v ffmpeg &> /dev/null; then
    echo "⚠️  FFmpeg nie jest zainstalowany!"
    echo "Instalacja FFmpeg..."

    if command -v apt &> /dev/null; then
        sudo apt update && sudo apt install -y ffmpeg
    elif command -v dnf &> /dev/null; then
        sudo dnf install -y ffmpeg
    elif command -v pacman &> /dev/null; then
        sudo pacman -S --noconfirm ffmpeg
    else
        echo "❌ Nie można automatycznie zainstalować FFmpeg"
        echo "Zainstaluj ręcznie: https://ffmpeg.org/download.html"
        exit 1
    fi
fi

echo "✅ FFmpeg zainstalowany: $(ffmpeg -version | head -n1)"

# Tworzenie wirtualnego środowiska
echo ""
echo "📦 Tworzenie wirtualnego środowiska..."
python3 -m venv .venv

# Aktywacja środowiska
echo "🔧 Aktywacja środowiska..."
source .venv/bin/activate

# Instalacja zależności
echo "📥 Instalacja zależności Python..."
pip install --upgrade pip
pip install -r requirements.txt

echo ""
echo "╔════════════════════════════════════════════════════════╗"
echo "║            ✅ INSTALACJA ZAKOŃCZONA!                   ║"
echo "╚════════════════════════════════════════════════════════╝"
echo ""
echo "🚀 Uruchom program:"
echo "   ./run_linux.sh"
echo ""
echo "📚 Dokumentacja:"
echo "   https://github.com/crahdlinuxservers-maker/YouTubeToMP3"
echo ""

