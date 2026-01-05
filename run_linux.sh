#!/bin/bash

# YouTube to MP3 Converter - Linux Run Script
# Author: Stanisław Kozioł

# Aktywacja środowiska wirtualnego
if [ ! -d ".venv" ]; then
    echo "❌ Wirtualne środowisko nie istnieje!"
    echo "Uruchom najpierw: ./install_linux.sh"
    exit 1
fi

source .venv/bin/activate

# Uruchomienie programu
echo "🚀 Uruchamianie YouTube to MP3 Converter..."
python3 youtube_to_mp3.py

# Deaktywacja środowiska po zakończeniu
deactivate

