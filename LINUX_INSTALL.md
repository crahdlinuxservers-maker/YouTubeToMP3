# 🐧 YouTube to MP3 Converter - Linux Installation Guide

## Szybka instalacja (Ubuntu/Debian)

```bash
# 1. Sklonuj repozytorium
git clone https://github.com/crahdlinuxservers-maker/YouTubeToMP3.git
cd YouTubeToMP3

# 2. Nadaj uprawnienia
chmod +x install_linux.sh run_linux.sh

# 3. Uruchom instalator
./install_linux.sh

# 4. Uruchom program
./run_linux.sh
```

## Co robi instalator?

`install_linux.sh` automatycznie:
- ✅ Sprawdza czy Python3 jest zainstalowany
- ✅ Instaluje FFmpeg (jeśli brakuje)
- ✅ Tworzy wirtualne środowisko Python
- ✅ Instaluje wszystkie wymagane biblioteki
- ✅ Przygotowuje program do uruchomienia

## Wymagania

### Minimalne
- **OS**: Dowolna dystrybucja Linuxa (kernel 4.0+)
- **Python**: 3.8 lub nowszy
- **RAM**: 512 MB (zalecane: 1 GB)
- **Miejsce**: 100 MB + miejsce na pobrane pliki

### Pakiety systemowe
Program automatycznie sprawdzi i zainstaluje (wymaga sudo):
- `python3`
- `python3-pip`
- `python3-venv`
- `python3-tk` (może wymagać ręcznej instalacji)
- `ffmpeg`

## Ręczna instalacja pakietów

### Ubuntu/Debian
```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv python3-tk ffmpeg git
```

### Fedora/RHEL/CentOS
```bash
sudo dnf install python3 python3-pip python3-tkinter ffmpeg git
```

### Arch Linux
```bash
sudo pacman -S python python-pip tk ffmpeg git
```

### openSUSE
```bash
sudo zypper install python3 python3-pip python3-tk ffmpeg git
```

## Rozwiązywanie problemów

### Błąd: "python3: command not found"
```bash
# Zainstaluj Python3
sudo apt install python3  # Ubuntu/Debian
sudo dnf install python3  # Fedora
sudo pacman -S python     # Arch
```

### Błąd: "tkinter module not found"
```bash
# Zainstaluj Tkinter
sudo apt install python3-tk        # Ubuntu/Debian
sudo dnf install python3-tkinter   # Fedora
sudo pacman -S tk                  # Arch
```

### Błąd: "ffmpeg: command not found"
```bash
# Zainstaluj FFmpeg
sudo apt install ffmpeg    # Ubuntu/Debian
sudo dnf install ffmpeg    # Fedora
sudo pacman -S ffmpeg      # Arch
```

### Błąd: "Permission denied"
```bash
# Nadaj uprawnienia wykonywania
chmod +x install_linux.sh run_linux.sh
```

### Program się nie uruchamia po instalacji
```bash
# Sprawdź logi
cat logs/youtube_converter_*.log

# Zrestartuj wirtualne środowisko
rm -rf .venv
./install_linux.sh
```

## Testowane dystrybucje

✅ **Ubuntu 20.04, 22.04, 24.04**  
✅ **Debian 11, 12**  
✅ **Fedora 38, 39, 40**  
✅ **Arch Linux** (rolling release)  
✅ **Linux Mint 21+**  
✅ **Pop!_OS 22.04+**  
✅ **Manjaro** (rolling release)  

## Używanie programu

Po instalacji:
```bash
# Uruchom program
./run_linux.sh

# Lub ręcznie
source .venv/bin/activate
python3 youtube_to_mp3.py
```

## Aktualizacja

```bash
# Pobierz najnowszą wersję
git pull origin master

# Zaktualizuj zależności
source .venv/bin/activate
pip install -r requirements.txt --upgrade
```

## Deinstalacja

```bash
# Usuń program
cd ..
rm -rf YouTubeToMP3

# (Opcjonalnie) Usuń FFmpeg jeśli nie jest używany
sudo apt remove ffmpeg        # Ubuntu/Debian
sudo dnf remove ffmpeg        # Fedora
sudo pacman -R ffmpeg         # Arch
```

## Wsparcie

- **GitHub Issues**: https://github.com/crahdlinuxservers-maker/YouTubeToMP3/issues
- **Dokumentacja**: https://github.com/crahdlinuxservers-maker/YouTubeToMP3
- **Autor**: Stanisław Kozioł

---

**Działa również na 🪟 Windows i 🍎 macOS!**

