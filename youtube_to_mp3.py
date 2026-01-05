"""
╔════════════════════════════════════════════════════════════════════════════╗
║                       YOUTUBE TO MP3 CONVERTER                             ║
║                        Konwerter YouTube → MP3                             ║
║                                                                             ║
║  Autor: Stanisław Kozioł                                                   ║
║  GitHub: https://github.com/crahdlinuxservers-maker/YouTubeToMP3           ║
║  Issues: https://github.com/crahdlinuxservers-maker/YouTubeToMP3/issues    ║
║                                                                             ║
║  Opis: Profesjonalny konwerter audio z GUI - pobiera muzykę z YouTube      ║
║        i konwertuje do MP3 z maksymalnym bitrate (320 kbps)               ║
║                                                                             ║
║  # HASH_YOUTUBE_CONVERTER: Główny moduł konwersji                          ║
║  # HASH_GUI_INTERFACE: Interfejs CustomTkinter                             ║
║  # KOMENTARZ PL: Program edukacyjny do nauki Pythona                       ║
╚════════════════════════════════════════════════════════════════════════════╝
"""

# ═══════════════════════════════════════════════════════════════════════════
# IMPORT BIBLIOTEK
# ═══════════════════════════════════════════════════════════════════════════

import customtkinter as ctk
from customtkinter import CTkLabel, CTkEntry, CTkButton, CTkProgressBar, CTkFrame, CTkImage
from tkinter import filedialog, messagebox
import threading
import os
import logging
from datetime import datetime
from pathlib import Path
import json
from io import BytesIO
from PIL import Image
import sqlite3
import time
import platform

# Dźwięki dla Windowsa
if platform.system() == "Windows":
    import winsound
    HAS_SOUND = True
else:
    HAS_SOUND = False
try:
    from yt_dlp import YoutubeDL
except ImportError:
    print("⚠️  Zainstaluj: pip install yt-dlp")
    exit(1)

try:
    import requests
    import zipfile
    import urllib.request
except ImportError:
    print("⚠️  Zainstaluj: pip install requests")
    exit(1)

try:
    from mutagen.id3 import ID3, TIT2, TPE1, APIC
    HAS_MUTAGEN = True
except ImportError:
    HAS_MUTAGEN = False
    logger_temp = logging.getLogger(__name__)
    logger_temp.warning("⚠️  mutagen nie zainstalowany - brak tagów ID3")

import sqlite3

# ═══════════════════════════════════════════════════════════════════════════
# KONFIGURACJA LOGOWANIA
# ═══════════════════════════════════════════════════════════════════════════

# HASH_LOGGING_CONFIG: Konfiguracja systemu logów
LOG_DIR = Path(__file__).parent / "logs"
LOG_DIR.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_DIR / f"youtube_converter_{datetime.now().strftime('%Y%m%d')}.log", encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════════════════════════
# KOLORY I TEMA
# ═══════════════════════════════════════════════════════════════════════════

# HASH_THEME_COLORS: Paleta kolorów aplikacji
THEME_COLORS = {
    "primary": "#1f1f1f",           # Ciemny tło
    "secondary": "#2a2a2a",         # Jaśniejszy ciemny
    "accent": "#ff0000",            # Czerwony YouTube
    "success": "#00ff00",           # Zielony sukces
    "warning": "#ffa500",           # Pomarańczowy ostrzeżenie
    "text_primary": "#ffffff",      # Biały tekst
    "text_secondary": "#b0b0b0",    # Szary tekst
    "bg_input": "#3a3a3a",          # Tło pola input
    "hover": "#ff3333"              # Hover efekt
}

# ═══════════════════════════════════════════════════════════════════════════
# KLASA TOOLTIP - Dymki z opisem przy najechaniu
# ═══════════════════════════════════════════════════════════════════════════

class ToolTip:
    """
    # KOMENTARZ PL: Tworzy przezroczyste dymki z opisem przy najechaniu na widget
    # HASH_TOOLTIP: Hover tooltips z opóźnieniem
    """
    def __init__(self, widget, text, delay=500):
        self.widget = widget
        self.text = text
        self.delay = delay  # Opóźnienie w ms
        self.tip_window = None
        self.schedule_id = None
        self.widget.bind("<Enter>", self.on_enter)
        self.widget.bind("<Leave>", self.on_leave)
        self.widget.bind("<Button>", self.on_leave)  # Ukryj przy kliknięciu

    def on_enter(self, event=None):
        """Zaplanuj wyświetlenie tooltipa z opóźnieniem"""
        self.schedule()

    def on_leave(self, event=None):
        """Anuluj i ukryj tooltip"""
        self.unschedule()
        self.hide_tip()

    def schedule(self):
        """Zaplanuj wyświetlenie tooltipa"""
        self.unschedule()
        self.schedule_id = self.widget.after(self.delay, self.show_tip)

    def unschedule(self):
        """Anuluj zaplanowane wyświetlenie"""
        if self.schedule_id:
            self.widget.after_cancel(self.schedule_id)
            self.schedule_id = None

    def show_tip(self):
        """Wyświetl tooltip"""
        if self.tip_window or not self.text:
            return

        try:
            # Pozycja dymka - wyśrodkowany nad widgetem
            x = self.widget.winfo_rootx() + self.widget.winfo_width() // 2
            y = self.widget.winfo_rooty() - 35

            # Stwórz okno tooltipa
            self.tip_window = tw = ctk.CTkToplevel(self.widget)
            tw.wm_overrideredirect(True)
            tw.wm_geometry(f"+{x}+{y}")
            tw.attributes('-topmost', True)

            # Wyłącz focus
            tw.attributes('-disabled', True)

            # Label z tekstem
            label = CTkLabel(
                tw,
                text=self.text,
                font=("Helvetica", 12),
                fg_color="#2b2b2b",
                text_color="#ffffff",
                corner_radius=6,
                padx=10,
                pady=5
            )
            label.pack()

            # Auto-ukryj po 3 sekundach (na wypadek gdyby Leave nie zadziałał)
            self.widget.after(3000, self.hide_tip)
        except:
            # Jeśli coś pójdzie nie tak, ukryj tooltip
            self.hide_tip()

    def hide_tip(self):
        """Ukryj tooltip"""
        if self.tip_window:
            try:
                self.tip_window.destroy()
            except:
                pass
            self.tip_window = None

# ═══════════════════════════════════════════════════════════════════════════
# KLASA ZARZĄDZANIA KONFIGURACJĄ
# ═══════════════════════════════════════════════════════════════════════════

class AppConfig:
    """
    # KOMENTARZ PL: Zarządza konfiguracją aplikacji (ostatni folder, motyw itp)
    # HASH_APP_CONFIG: Plik konfiguracyjny JSON
    """

    def __init__(self):
        self.config_path = Path(__file__).parent / "app_config.json"
        self.defaults = {
            'last_folder': str(Path.home() / "Pobrane" / "YouTube_MP3"),
            'theme': 'dark',  # dark / light
            'sound_enabled': True,
            'auto_start': False
        }
        self.config = self.load_config()

    def load_config(self):
        """Ładuje konfigurację z pliku"""
        try:
            if self.config_path.exists():
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    return {**self.defaults, **config}
        except Exception as e:
            logger.warning(f"⚠️ Nie można załadować konfiguracji: {str(e)}")
        return self.defaults.copy()

    def save_config(self):
        """Zapisuje konfigurację do pliku"""
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
                logger.info("✅ Konfiguracja zapisana")
        except Exception as e:
            logger.error(f"❌ Błąd zapisywania konfiguracji: {str(e)}")

    def get(self, key, default=None):
        """Pobiera wartość z konfiguracji"""
        return self.config.get(key, default)

    def set(self, key, value):
        """Ustawia wartość w konfiguracji"""
        self.config[key] = value
        self.save_config()

# ═══════════════════════════════════════════════════════════════════════════
# KLASA ZARZĄDZANIA DŹWIĘKAMI
# ═══════════════════════════════════════════════════════════════════════════

class SoundManager:
    """
    # KOMENTARZ PL: Zarządza dźwiękami powiadomień
    # HASH_SOUND_MANAGER: Powiadomienia dźwiękowe
    """

    @staticmethod
    def play_sound(sound_type='complete'):
        """Gra dźwięk powiadomienia"""
        if not HAS_SOUND:
            return

        try:
            frequencies = {
                'complete': (1000, 500),  # (Hz, ms)
                'error': (400, 300),
                'start': (800, 200)
            }

            freq, duration = frequencies.get(sound_type, (1000, 300))
            winsound.Beep(freq, duration)
            logger.info(f"🔊 Dźwięk: {sound_type}")
        except Exception as e:
            logger.warning(f"⚠️ Nie można zagrać dźwięku: {str(e)}")

# ═══════════════════════════════════════════════════════════════════════════
# KLASA KONTROLI PAUZY KONWERSJI
# ═══════════════════════════════════════════════════════════════════════════

class ConversionPauser:
    """
    # KOMENTARZ PL: Zarządza pauzą i wznowieniem konwersji
    # HASH_CONVERSION_PAUSER: Pauza/Wznowienie
    """

    def __init__(self):
        self.is_paused = False
        self.pause_event = threading.Event()
        self.pause_event.set()  # Nie spauzowan

    def pause(self):
        """Pauzuje konwersję"""
        self.is_paused = True
        self.pause_event.clear()
        logger.info("⏸️ Konwersja wstrzymana")

    def resume(self):
        """Wznawia konwersję"""
        self.is_paused = False
        self.pause_event.set()
        logger.info("▶️ Konwersja wznowiona")

    def check_pause(self):
        """Czeka jeśli konwersja jest spauzowan"""
        self.pause_event.wait()

# ═══════════════════════════════════════════════════════════════════════════
# KLASA ZARZĄDZANIA HISTORIĄ POBRAŃ
# ═══════════════════════════════════════════════════════════════════════════

class DownloadHistory:
    """
    # KOMENTARZ PL: Zarządza historią pobrań i statystykami
    # HASH_DOWNLOAD_HISTORY: Baza danych SQLite
    """

    def __init__(self):
        self.db_path = Path(__file__).parent / "download_history.db"
        self.init_database()

    def init_database(self):
        """Inicjalizuje bazę danych"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS downloads (
                        id INTEGER PRIMARY KEY,
                        title TEXT NOT NULL,
                        url TEXT NOT NULL,
                        format TEXT,
                        file_size INTEGER,
                        download_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                conn.commit()
                logger.info("✅ Baza danych historii zainicjalizowana")
        except Exception as e:
            logger.error(f"❌ Błąd inicjalizacji bazy danych: {str(e)}")

    def add_download(self, title: str, url: str, format_type: str = "mp3", file_size: int = 0):
        """Dodaje wpis do historii"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO downloads (title, url, format, file_size)
                    VALUES (?, ?, ?, ?)
                ''', (title, url, format_type, file_size))
                conn.commit()
                logger.info(f"📝 Dodano do historii: {title}")
        except Exception as e:
            logger.error(f"❌ Błąd dodawania do historii: {str(e)}")

    def get_history(self, limit: int = 100) -> list:
        """Pobiera historię pobrań"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT title, download_date, format, file_size
                    FROM downloads
                    ORDER BY download_date DESC
                    LIMIT ?
                ''', (limit,))
                return cursor.fetchall()
        except Exception as e:
            logger.error(f"❌ Błąd pobierania historii: {str(e)}")
            return []

    def get_statistics(self) -> dict:
        """Pobiera statystyki"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                # Liczba pobrań
                cursor.execute("SELECT COUNT(*) FROM downloads")
                total_downloads = cursor.fetchone()[0]

                # Całkowity rozmiar
                cursor.execute("SELECT SUM(file_size) FROM downloads WHERE file_size > 0")
                total_size = cursor.fetchone()[0] or 0

                # Ulubiony format
                cursor.execute('''
                    SELECT format, COUNT(*) as count
                    FROM downloads
                    GROUP BY format
                    ORDER BY count DESC
                    LIMIT 1
                ''')
                fav_format = cursor.fetchone()

                return {
                    'total_downloads': total_downloads,
                    'total_size_mb': round(total_size / (1024 * 1024), 2),
                    'favorite_format': fav_format[0] if fav_format else 'mp3'
                }
        except Exception as e:
            logger.error(f"❌ Błąd pobierania statystyk: {str(e)}")
            return {'total_downloads': 0, 'total_size_mb': 0, 'favorite_format': 'mp3'}

    def clear_history(self):
        """Czyści historię"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM downloads")
                conn.commit()
                logger.info("🗑️ Historia czyszczona")
        except Exception as e:
            logger.error(f"❌ Błąd czyszczenia historii: {str(e)}")

# ═══════════════════════════════════════════════════════════════════════════
# KLASA ZARZĄDZANIA FFMPEG
# ═══════════════════════════════════════════════════════════════════════════

class FFmpegManager:
    """
    # KOMENTARZ PL: Zarządza instalacją i konfiguracją FFmpeg
    # HASH_FFMPEG_MANAGER: Automatyczne pobieranie FFmpeg
    """

    def __init__(self):
        self.ffmpeg_dir = Path(__file__).parent / "ffmpeg"
        self.ffmpeg_exe = self.ffmpeg_dir / "ffmpeg.exe"
        self.ffprobe_exe = self.ffmpeg_dir / "ffprobe.exe"

    def is_ffmpeg_available(self) -> bool:
        """Sprawdza czy FFmpeg jest dostępny"""
        return self.ffmpeg_exe.exists() and self.ffprobe_exe.exists()

    def download_ffmpeg(self, progress_callback=None) -> bool:
        """
        # KOMENTARZ PL: Pobiera i instaluje FFmpeg
        # HASH_FFMPEG_DOWNLOAD: Pobieranie z GitHub releases
        """
        try:
            logger.info("📥 Pobieranie FFmpeg...")

            # URL do FFmpeg (wersja essentials)
            ffmpeg_url = "https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip"

            # Stwórz folder
            self.ffmpeg_dir.mkdir(exist_ok=True)
            zip_path = self.ffmpeg_dir / "ffmpeg.zip"

            # Pobierz plik
            logger.info("📁 Pobieranie pliku ZIP...")
            urllib.request.urlretrieve(ffmpeg_url, zip_path)

            # Wypakuj
            logger.info("📂 Wypakowywanie...")
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                # Znajdź binaries
                for file_info in zip_ref.filelist:
                    if file_info.filename.endswith('ffmpeg.exe'):
                        # Wypakuj ffmpeg.exe
                        with zip_ref.open(file_info) as source:
                            with open(self.ffmpeg_exe, 'wb') as target:
                                target.write(source.read())
                    elif file_info.filename.endswith('ffprobe.exe'):
                        # Wypakuj ffprobe.exe
                        with zip_ref.open(file_info) as source:
                            with open(self.ffprobe_exe, 'wb') as target:
                                target.write(source.read())

            # Usuń ZIP
            zip_path.unlink()

            logger.info("✅ FFmpeg zainstalowany pomyślnie!")
            return True

        except Exception as e:
            logger.error(f"❌ Błąd instalacji FFmpeg: {str(e)}")
            return False

    def get_ffmpeg_path(self) -> str:
        """Zwraca ścieżkę do FFmpeg"""
        return str(self.ffmpeg_dir)

# ═══════════════════════════════════════════════════════════════════════════
# KLASA KONWERTERA
# ═══════════════════════════════════════════════════════════════════════════

class YouTubeToMP3Converter:
    """
    # KOMENTARZ PL: Główna klasa do konwersji YouTube na MP3
    # HASH_CONVERTER_CORE: Logika pobierania i konwersji
    """

    def __init__(self, output_path: str = None):
        """
        Inicjalizacja konwertera

        Args:
            output_path: Ścieżka do folderu docelowego
        """
        self.output_path = output_path or str(Path.home() / "Pobrane" / "YouTube_MP3")
        Path(self.output_path).mkdir(parents=True, exist_ok=True)
        self.is_converting = False
        self.ffmpeg_manager = FFmpegManager()

        # Sprawdź FFmpeg
        if not self.ffmpeg_manager.is_ffmpeg_available():
            logger.warning("⚠️  FFmpeg nie jest dostępny - zostanie pobrany automatycznie")

        logger.info(f"🎵 Konwerter zainicjalizowany. Folder: {self.output_path}")

    def get_video_info(self, url: str) -> dict:
        """
        # KOMENTARZ PL: Pobiera informacje o wideo
        # HASH_VIDEO_INFO: Metoda do uzyskania metadanych
        """
        try:
            logger.info(f"🔍 Pobieranie informacji o wideo: {url}")

            # Sprawdź czy to link do playlisty (bez konkretnego wideo)
            is_playlist_url = 'playlist?list=' in url or '/playlists/' in url

            if is_playlist_url:
                # TO JEST PLAYLISTA - użyj extract_flat dla szybkości
                logger.info("📋 Wykryto URL playlisty")
                ydl_opts = {
                    'quiet': True,
                    'no_warnings': True,
                    'socket_timeout': 15,
                    'skip_download': True,
                    'extract_flat': 'in_playlist',  # Szybko dla playlist
                    'ignoreerrors': True,
                    'http_headers': {
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                    }
                }
            else:
                # POJEDYNCZE WIDEO - pełne metadane
                logger.info("📹 Wykryto URL pojedynczego wideo")
                ydl_opts = {
                    'quiet': True,
                    'no_warnings': True,
                    'socket_timeout': 15,
                    'skip_download': True,
                    'no_color': True,
                    'extract_flat': False,  # Potrzebujemy pełnych info dla miniatury
                    'noplaylist': True,  # WYMUSZAJ pojedyncze wideo, nawet jeśli w linku jest ?list=
                    'ignoreerrors': True,
                    'youtube_include_dash_manifest': False,  # Przyspiesza
                    'no_check_certificate': True,  # Przyspiesza
                    'http_headers': {
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                    }
                }

            with YoutubeDL(ydl_opts) as ydl:
                logger.info("📥 Łączenie z YouTube...")
                info = ydl.extract_info(url, download=False)

                # Sprawdź czy to playlista
                is_playlist = info.get('_type') == 'playlist'

                # Fallback: sprawdź czy ma entries (to oznacza playlistę)
                if not is_playlist and 'entries' in info:
                    is_playlist = len(info.get('entries', [])) > 1
                    logger.info(f"📋 Wykryto playlistę po entries: {len(info.get('entries', []))} wideo")

                if is_playlist:
                    playlist_title = info.get('title', 'Unknown Playlist')
                    entries = info.get('entries', [])
                    playlist_count = len(entries) if entries else 0

                    logger.info(f"📋 Playlista znaleziona: {playlist_title}")
                    logger.info(f"   Liczba wideo: {playlist_count}")

                    return {
                        'title': playlist_title,
                        'duration': 0,
                        'thumbnail': '',
                        'channel': info.get('uploader', 'Unknown'),
                        'valid': True,
                        'is_playlist': True,
                        'playlist_count': playlist_count
                    }
                else:
                    title = info.get('title', 'Unknown')
                    duration = info.get('duration', 0)
                    thumbnail = info.get('thumbnail', '')
                    channel = info.get('uploader', info.get('channel', 'Unknown'))

                    logger.info(f"✅ Wideo znalezione: {title}")
                    logger.info(f"   Kanał: {channel}, Długość: {duration}s")
                    if thumbnail:
                        logger.info(f"   Miniatura: OK")
                    else:
                        logger.warning(f"   Miniatura: BRAK")

                    return {
                        'title': title,
                        'duration': duration,
                        'thumbnail': thumbnail,
                        'channel': channel,
                        'valid': True,
                        'is_playlist': False,
                        'playlist_count': 0
                    }
        except Exception as e:
            error_msg = str(e)
            logger.error(f"❌ Błąd pobierania informacji: {error_msg}")
            return {
                'valid': False,
                'error': f"Błąd: {error_msg}"
            }

    def convert(self, url: str, progress_callback=None, bitrate: str = "320", allow_playlist: bool = False, format_type: str = "mp3") -> bool:
        """
        # KOMENTARZ PL: Konwertuje YouTube na audio
        # HASH_CONVERSION_PROCESS: Główny proces konwersji

        Args:
            url: Link do YouTube
            progress_callback: Funkcja callback do aktualizacji paska postępu
            bitrate: Jakość audio w kbps (128, 192, 256, 320)
            allow_playlist: Czy pozwolić na pobieranie całej playlisty
            format_type: Format wyjściowy (mp3, m4a, wav, ogg, flac)

        Returns:
            bool: Sukces/niepowodzenie
        """
        try:
            self.is_converting = True
            playlist_info = " (Playlista)" if allow_playlist else ""
            logger.info(f"▶️  Rozpoczęto konwersję: {url} | Bitrate: {bitrate} kbps | Format: {format_type}{playlist_info}")

            # Sprawdź i pobierz FFmpeg jeśli potrzeba
            if not self.ffmpeg_manager.is_ffmpeg_available():
                logger.info("📥 Pobieranie FFmpeg...")
                if progress_callback:
                    progress_callback(0.1)

                if not self.ffmpeg_manager.download_ffmpeg():
                    logger.error("❌ Nie udało się pobrać FFmpeg")
                    return False

            if progress_callback:
                # Wywołaj callback z danymi (dict lub float - kompatybilność)
                try:
                    progress_callback({'percentage': 20.0, 'speed': 0, 'eta': 0, 'downloaded': 0})
                except:
                    # Fallback dla starych callbacków oczekujących float
                    try:
                        progress_callback(0.2)
                    except:
                        pass

            # Mapowanie formatów do codeców
            format_map = {
                'mp3': ('mp3', bitrate),
                'm4a': ('m4a', 'auto'),
                'wav': ('wav', 'pcm_s16le'),
                'ogg': ('vorbis', bitrate),
                'flac': ('flac', 'pcm_s16le')
            }

            codec, quality = format_map.get(format_type, ('mp3', bitrate))

            # HASH_YDLP_CONFIG: Konfiguracja yt-dlp z FFmpeg
            ydl_opts = {
                'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': codec,
                    'preferredquality': quality,
                }],
                'outtmpl': os.path.join(self.output_path, '%(title)s.%(ext)s'),
                'quiet': False,
                'no_warnings': False,
                'progress_hooks': [self._progress_hook] if progress_callback else [],
                'socket_timeout': 30,
                'ffmpeg_location': self.ffmpeg_manager.get_ffmpeg_path(),  # Ścieżka do FFmpeg
                'noplaylist': not allow_playlist,  # Pozwól na playlist jeśli allow_playlist=True
            }

            # KOMENTARZ PL: Przechowaj callback dla progresu
            self._progress_callback = progress_callback

            with YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                title = info.get('title', 'Unknown')

            logger.info(f"✅ Konwersja zakończona: {title}")
            self.is_converting = False
            return True

        except Exception as e:
            logger.error(f"❌ Błąd konwersji: {str(e)}")
            self.is_converting = False
            return False

    def _progress_hook(self, d):
        """
        # KOMENTARZ PL: Hook do aktualizacji postępu
        # HASH_PROGRESS_HOOK: Callback dla paska postępu
        """
        if not self._progress_callback:
            return

        try:
            if d['status'] == 'downloading':
                # Przygotuj pełne dane dla callback
                data = {}

                # Procent
                percent_str = d.get('_percent_str', '0%').strip().replace('%', '')
                try:
                    data['percentage'] = float(percent_str)
                except:
                    data['percentage'] = 0.0

                # Prędkość (bajty/s)
                data['speed'] = d.get('speed', 0) or 0

                # ETA (sekundy)
                data['eta'] = d.get('eta', 0) or 0

                # Pobrane (bajty)
                data['downloaded'] = d.get('downloaded_bytes', 0) or 0

                # Wywołaj callback z danymi
                self._progress_callback(data)

            elif d['status'] == 'finished':
                # 100% ukończone
                data = {
                    'percentage': 100.0,
                    'speed': 0,
                    'eta': 0,
                    'downloaded': d.get('total_bytes', 0) or 0
                }
                self._progress_callback(data)
        except Exception as e:
            logger.warning(f"⚠️ Błąd w progress_hook: {str(e)}")

    def add_id3_tags(self, file_path: str, title: str, artist: str = "", thumbnail_url: str = ""):
        """
        # KOMENTARZ PL: Dodaje tagi ID3 do pliku MP3
        # HASH_ID3_TAGS: Metadane audio
        """
        if not HAS_MUTAGEN or not file_path.endswith('.mp3'):
            return

        try:
            logger.info(f"🏷️ Dodawanie ID3 tagów: {title}")

            # Załaduj lub stwórz tagi
            try:
                tags = ID3(file_path)
            except:
                tags = ID3()

            # Dodaj tytuł
            tags['TIT2'] = TIT2(encoding=3, text=title)

            # Dodaj artystę
            if artist:
                tags['TPE1'] = TPE1(encoding=3, text=artist)

            # Dodaj okładkę (thumbnail)
            if thumbnail_url:
                try:
                    response = requests.get(thumbnail_url, timeout=5)
                    if response.status_code == 200:
                        tags['APIC'] = APIC(
                            encoding=3,
                            mime='image/jpeg',
                            type=3,
                            desc='Cover',
                            data=response.content
                        )
                        logger.info("✅ Okładka dodana do ID3")
                except Exception as e:
                    logger.warning(f"⚠️ Nie można dodać okładki: {str(e)}")

            # Zapisz tagi
            tags.save(file_path)
            logger.info(f"✅ ID3 tagi dodane: {title}")

        except Exception as e:
            logger.warning(f"⚠️ Nie można dodać ID3 tagów: {str(e)}")

# ═══════════════════════════════════════════════════════════════════════════
# GŁÓWNA APLIKACJA GUI
# ═══════════════════════════════════════════════════════════════════════════

class YouTubeMP3App(ctk.CTk):
    """
    # KOMENTARZ PL: Główna klasa aplikacji z GUI
    # HASH_GUI_APPLICATION: Interfejs CustomTkinter
    """

    def __init__(self):
        super().__init__()

        # HASH_WINDOW_CONFIG: Konfiguracja okna
        self.title("🎵 YouTube to MP3 Converter | Autor: Stanisław Kozioł")
        self.geometry("700x700")
        self.minsize(700, 590)
        self.maxsize(700, 590)
        self.resizable(False, False)

        # Ustaw motyw
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")

        # HASH_UI_INITIALIZATION: Inicjalizacja UI
        self.app_config = AppConfig()
        self.sound_manager = SoundManager()
        self.pauser = ConversionPauser()

        self.converter = None
        self.output_folder = self.app_config.get('last_folder', str(Path.home() / "Pobrane" / "YouTube_MP3"))
        self.is_converting = False
        self.ffmpeg_manager = FFmpegManager()
        self.download_history = DownloadHistory()
        self.is_playlist = False
        self.playlist_count = 0
        self.current_thumbnail = None
        self.last_url = ""  # Dla auto-sprawdzania
        self.selected_format = "mp3"  # Domyślny format
        self.selected_playlist_videos = None  # Wybrane wideo z playlisty

        # Zmienne dla danych postępu (dla nerda)
        self.progress_start_time = 0
        self.progress_last_update = 0
        self.progress_downloaded = 0

        # Stwórz UI
        self.setup_ui()

        # Sprawdź FFmpeg po uruchomieniu
        self.check_ffmpeg_status()

        logger.info("🚀 Aplikacja uruchomiona")

    def setup_ui(self):
        """
        # KOMENTARZ PL: Buduje interfejs użytkownika
        # HASH_UI_LAYOUT: Układ interfejsu
        """

        # ═══════════════════════════════════════════════════════════════════
        # GŁÓWNY FRAME
        # ═══════════════════════════════════════════════════════════════════

        main_frame = CTkFrame(self, fg_color=THEME_COLORS["primary"])
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # ═══════════════════════════════════════════════════════════════════
        # NAGŁÓWEK
        # ═══════════════════════════════════════════════════════════════════

        header_frame = CTkFrame(main_frame, fg_color=THEME_COLORS["accent"], height=45)
        header_frame.pack(fill="x", pady=(0, 4))

        # Container dla tytułu i ikony autora
        header_content = CTkFrame(header_frame, fg_color="transparent")
        header_content.pack(fill="both", expand=True)

        # Tytuł (po lewej/środek)
        title_container = CTkFrame(header_content, fg_color="transparent")
        title_container.pack(side="left", expand=True, fill="both")

        title_label = CTkLabel(
            title_container,
            text="🎵 YouTube to MP3 Converter",
            font=("Helvetica", 16, "bold"),
            text_color=THEME_COLORS["text_primary"]
        )
        title_label.pack(pady=4)

        subtitle_label = CTkLabel(
            title_container,
            text="Pobierz muzykę z YouTube",
            font=("Helvetica", 12),
            text_color=THEME_COLORS["text_secondary"]
        )
        subtitle_label.pack(pady=(0, 2))

        # Ikona "O autorze" (po prawej)
        author_btn = CTkButton(
            header_content,
            text="👤",
            command=self.show_about,
            height=35,
            width=35,
            font=("Helvetica", 16),
            fg_color="#ff9933",
            hover_color="#ffaa55",
            text_color=THEME_COLORS["text_primary"],
            corner_radius=8,
            border_width=0
        )
        author_btn.pack(side="right", padx=8, pady=4)
        ToolTip(author_btn, "Informacje o autorze i programie")

        # ═══════════════════════════════════════════════════════════════════
        # SEKCJA LINKU
        # ═══════════════════════════════════════════════════════════════════

        url_frame = CTkFrame(main_frame, fg_color=THEME_COLORS["secondary"], corner_radius=8)
        url_frame.pack(fill="x", pady=2)

        url_label = CTkLabel(
            url_frame,
            text="🔗 Link YouTube:",
            font=("Helvetica", 12, "bold"),
            text_color=THEME_COLORS["text_primary"]
        )
        url_label.pack(anchor="w", padx=12, pady=(6, 2))

        # HASH_URL_ENTRY: Pole wejściowe na URL z przyciskiem Sprawdź
        url_input_frame = CTkFrame(url_frame, fg_color="transparent")
        url_input_frame.pack(fill="x", padx=12, pady=(2, 6))

        self.url_entry = CTkEntry(
            url_input_frame,
            placeholder_text="Wklej link YouTube...",
            height=32,
            font=("Helvetica", 12),
            fg_color=THEME_COLORS["bg_input"],
            border_color=THEME_COLORS["accent"],
            border_width=2,
            text_color=THEME_COLORS["text_primary"]
        )
        self.url_entry.pack(side="left", fill="both", expand=True, padx=(0, 8))
        # Podłącz auto-sprawdzanie przy wklejeniu (Ctrl+V)
        self.url_entry.bind('<KeyRelease>', self.on_url_change)
        # Drag & Drop - obsługa wklejenia przez przeciągnięcie
        self.url_entry.bind('<Control-v>', self.on_url_change)
        self.url_entry.bind('<Command-v>', self.on_url_change)  # macOS


        # ═══════════════════════════════════════════════════════════════════
        # SEKCJA INFORMACJI (z miniaturą)
        # ═══════════════════════════════════════════════════════════════════

        info_frame = CTkFrame(main_frame, fg_color=THEME_COLORS["secondary"], corner_radius=8, height=105)
        info_frame.pack(fill="x", pady=2)
        info_frame.pack_propagate(False)  # Zachowaj stałą wysokość

        # Kontener poziomy na miniaturę i tekst
        info_content = CTkFrame(info_frame, fg_color="transparent")
        info_content.pack(fill="both", expand=True, padx=8, pady=6)

        # HASH_THUMBNAIL: Miniatura wideo (lewa strona)
        self.thumbnail_label = CTkLabel(
            info_content,
            text="🎬",
            width=105,
            height=95,
            fg_color=THEME_COLORS["bg_input"],
            corner_radius=8,
            font=("Helvetica", 32),
            text_color=THEME_COLORS["text_secondary"]
        )
        self.thumbnail_label.pack(side="left", padx=(2, 8))

        # Tekstowe info (prawa strona) - poprawa wizualna
        info_text_frame = CTkFrame(info_content, fg_color="transparent")
        info_text_frame.pack(side="left", fill="both", expand=True, padx=(0, 4))

        # HASH_INFO_DISPLAY: Wyświetlanie informacji - z lepszą typografią
        self.info_display = CTkLabel(
            info_text_frame,
            text="📹 Wklej link YouTube\n⚡ Automatyczne sprawdzenie",
            font=("Helvetica", 12),
            text_color=THEME_COLORS["text_secondary"],
            justify="left",
            wraplength=380
        )
        self.info_display.pack(anchor="w", fill="both", expand=True, pady=2)

        # ═══════════════════════════════════════════════════════════════════
        # MODUŁ PLAYLISTY (prawa strona - elegancka ikona)
        # ═══════════════════════════════════════════════════════════════════

        playlist_module = CTkFrame(
            info_content,
            fg_color="#1a1a1a",
            corner_radius=12,
            border_width=0,
            width=120,
            height=95
        )
        playlist_module.pack(side="right", padx=(4, 2))
        playlist_module.pack_propagate(False)

        # Ikona playlisty - duża i wyraźna
        playlist_icon = CTkLabel(
            playlist_module,
            text="📋",
            font=("Helvetica", 36),
            text_color=THEME_COLORS["warning"],
            fg_color="transparent"
        )
        playlist_icon.pack(pady=(8, 0))

        # HASH_PLAYLIST_CHECKBOX: Checkbox dla playlist - wyraźny i duży
        self.playlist_var = ctk.BooleanVar(value=False)
        self.playlist_checkbox = ctk.CTkCheckBox(
            playlist_module,
            text="Playlista",
            variable=self.playlist_var,
            font=("Helvetica", 12, "bold"),
            fg_color=THEME_COLORS["warning"],
            hover_color="#ffb84d",
            text_color=THEME_COLORS["text_primary"],
            border_color=THEME_COLORS["warning"],
            border_width=2,
            checkbox_width=18,
            checkbox_height=18,
            corner_radius=4
        )
        self.playlist_checkbox.pack(pady=(2, 2))
        ToolTip(self.playlist_checkbox, "Zaznacz i kliknij KONWERTUJ aby pobrać playlistę")

        # Info o trybie playlisty
        playlist_info = CTkLabel(
            playlist_module,
            text="⚡ Masowe",
            font=("Helvetica", 12),
            text_color=THEME_COLORS["text_secondary"],
            fg_color="transparent",
            justify="center"
        )
        playlist_info.pack(pady=(0, 6))

        # ═══════════════════════════════════════════════════════════════════
        # SEKCJA POSTĘPU (pod Info)
        # ═══════════════════════════════════════════════════════════════════

        progress_frame = CTkFrame(main_frame, fg_color=THEME_COLORS["secondary"], corner_radius=8)
        progress_frame.pack(fill="x", pady=2)

        # HASH_PROGRESS_LABEL: Główny pasek postępu
        self.progress_bar = CTkProgressBar(
            progress_frame,
            height=14,
            fg_color=THEME_COLORS["bg_input"],
            progress_color=THEME_COLORS["accent"],
            corner_radius=6
        )
        self.progress_bar.pack(fill="x", padx=10, pady=(6, 2))
        self.progress_bar.set(0)

        # Linia z danymi dla nerda
        progress_data_frame = CTkFrame(progress_frame, fg_color="transparent")
        progress_data_frame.pack(fill="x", padx=10, pady=(0, 6))

        # Procent
        self.progress_percent_label = CTkLabel(
            progress_data_frame,
            text="0%",
            font=("Helvetica", 12, "bold"),
            text_color=THEME_COLORS["text_primary"]
        )
        self.progress_percent_label.pack(side="left", padx=(0, 8))

        # Status
        self.progress_status_label = CTkLabel(
            progress_data_frame,
            text="Gotowy",
            font=("Helvetica", 12),
            text_color=THEME_COLORS["text_secondary"]
        )
        self.progress_status_label.pack(side="left", padx=(0, 12))

        # Rozmiar pobierany
        self.progress_size_label = CTkLabel(
            progress_data_frame,
            text="0 MB",
            font=("Helvetica", 12),
            text_color=THEME_COLORS["text_secondary"]
        )
        self.progress_size_label.pack(side="left", padx=(0, 12))

        # Szybkość
        self.progress_speed_label = CTkLabel(
            progress_data_frame,
            text="0 MB/s",
            font=("Helvetica", 12),
            text_color=THEME_COLORS["text_secondary"]
        )
        self.progress_speed_label.pack(side="left", padx=(0, 12))

        # ETA
        self.progress_eta_label = CTkLabel(
            progress_data_frame,
            text="--:--",
            font=("Helvetica", 12),
            text_color=THEME_COLORS["text_secondary"]
        )
        self.progress_eta_label.pack(side="left")

        folder_frame = CTkFrame(main_frame, fg_color=THEME_COLORS["secondary"], corner_radius=8)
        folder_frame.pack(fill="x", pady=2)

        folder_label = CTkLabel(
            folder_frame,
            text="📁 Folder:",
            font=("Helvetica", 12, "bold"),
            text_color=THEME_COLORS["text_primary"]
        )
        folder_label.pack(anchor="w", padx=12, pady=(4, 1))

        # HASH_FOLDER_DISPLAY: Wyświetlanie ścieżki folderu
        self.folder_display = CTkLabel(
            folder_frame,
            text=self.output_folder,
            font=("Helvetica", 12),
            text_color=THEME_COLORS["text_secondary"],
            wraplength=400,
            justify="left"
        )
        self.folder_display.pack(anchor="w", padx=12, pady=(0, 3))

        # Przyciski folder i FFmpeg
        btn_frame_row = CTkFrame(folder_frame, fg_color="transparent")
        btn_frame_row.pack(fill="x", padx=12, pady=(0, 4))

        btn_select_folder = CTkButton(
            btn_frame_row,
            text="📂 Folder",
            command=self.select_folder,
            height=24,
            font=("Helvetica", 12, "bold"),
            fg_color=THEME_COLORS["accent"],
            hover_color=THEME_COLORS["hover"],
            text_color=THEME_COLORS["text_primary"],
            corner_radius=6
        )
        btn_select_folder.pack(side="left", fill="both", expand=True, padx=(0, 3))

        # Przycisk instalacji FFmpeg
        self.btn_install_ffmpeg = CTkButton(
            btn_frame_row,
            text="🔧 FFmpeg",
            command=self.install_ffmpeg,
            height=24,
            font=("Helvetica", 12, "bold"),
            fg_color=THEME_COLORS["warning"],
            hover_color="#ffb84d",
            text_color=THEME_COLORS["primary"],
            corner_radius=6
        )
        self.btn_install_ffmpeg.pack(side="left", fill="both", expand=True)

        # ═══════════════════════════════════════════════════════════════════
        # SEKCJA JAKOŚCI I FORMATU AUDIO (obok siebie)
        # ═══════════════════════════════════════════════════════════════════

        audio_settings_frame = CTkFrame(main_frame, fg_color="transparent")
        audio_settings_frame.pack(fill="x", pady=2)

        # ═══════════════════════════════════════════════════════════════════
        # LEWA STRONA: JAKOŚĆ AUDIO
        # ═══════════════════════════════════════════════════════════════════

        quality_frame = CTkFrame(audio_settings_frame, fg_color=THEME_COLORS["secondary"], corner_radius=8)
        quality_frame.pack(side="left", fill="both", expand=True, padx=(0, 2))

        quality_label = CTkLabel(
            quality_frame,
            text="🎵 Jakość:",
            font=("Helvetica", 12, "bold"),
            text_color=THEME_COLORS["text_primary"]
        )
        quality_label.pack(anchor="w", padx=8, pady=(4, 1))

        # HASH_QUALITY_SELECTOR: Dropdown wyboru jakości
        quality_selector_frame = CTkFrame(quality_frame, fg_color="transparent")
        quality_selector_frame.pack(fill="x", padx=8, pady=(0, 3))

        self.quality_var = ctk.StringVar(value="320 kbps (Najwyższa)")
        self.quality_selector = ctk.CTkComboBox(
            quality_selector_frame,
            values=[
                "128 kbps (Dobra)",
                "192 kbps (Bardzo dobra)",
                "256 kbps (Wysoka)",
                "320 kbps (Najwyższa)"
            ],
            variable=self.quality_var,
            font=("Helvetica", 12),
            dropdown_font=("Helvetica", 12),
            fg_color=THEME_COLORS["bg_input"],
            border_color=THEME_COLORS["accent"],
            button_color=THEME_COLORS["accent"],
            button_hover_color=THEME_COLORS["hover"],
            dropdown_fg_color=THEME_COLORS["secondary"],
            dropdown_hover_color=THEME_COLORS["accent"],
            text_color=THEME_COLORS["text_primary"],
            state="readonly",
            width=150,
            height=24
        )
        self.quality_selector.pack(fill="x")

        # Info o rozmiarze
        self.quality_info = CTkLabel(
            quality_frame,
            text="≈ 3-4 MB/min",
            font=("Helvetica", 7),
            text_color=THEME_COLORS["text_secondary"]
        )
        self.quality_info.pack(anchor="w", padx=8, pady=(1, 3))


        # ═══════════════════════════════════════════════════════════════════
        # PRAWA STRONA: FORMAT AUDIO
        # ═══════════════════════════════════════════════════════════════════

        format_frame = CTkFrame(audio_settings_frame, fg_color=THEME_COLORS["secondary"], corner_radius=8)
        format_frame.pack(side="left", fill="both", expand=True, padx=(2, 0))

        format_label = CTkLabel(
            format_frame,
            text="🎵 Format:",
            font=("Helvetica", 12, "bold"),
            text_color=THEME_COLORS["text_primary"]
        )
        format_label.pack(anchor="w", padx=8, pady=(4, 1))

        # Selektor formatu
        format_selector_frame = CTkFrame(format_frame, fg_color="transparent")
        format_selector_frame.pack(fill="x", padx=8, pady=(0, 3))

        self.format_var = ctk.StringVar(value="MP3 (MPEG Audio)")
        self.format_selector = ctk.CTkComboBox(
            format_selector_frame,
            values=["MP3 (MPEG)", "M4A (AAC)", "WAV (PCM)", "OGG (Vorbis)", "FLAC"],
            variable=self.format_var,
            font=("Helvetica", 12),
            dropdown_font=("Helvetica", 12),
            fg_color=THEME_COLORS["bg_input"],
            border_color=THEME_COLORS["accent"],
            button_color=THEME_COLORS["accent"],
            button_hover_color=THEME_COLORS["hover"],
            dropdown_fg_color=THEME_COLORS["secondary"],
            dropdown_hover_color=THEME_COLORS["accent"],
            text_color=THEME_COLORS["text_primary"],
            state="readonly",
            width=100,
            height=24
        )
        self.format_selector.pack(side="left", fill="both", expand=True)
        self.format_selector.configure(command=self.on_format_change)
        ToolTip(self.format_selector, "Wybierz format pliku audio\nMP3 = najbardziej kompatybilny")

        # Przycisk statystyk
        self.btn_stats = CTkButton(
            format_selector_frame,
            text="📊",
            command=self.show_statistics,
            height=24,
            font=("Helvetica", 12, "bold"),
            fg_color=THEME_COLORS["warning"],
            hover_color="#ffb84d",
            text_color=THEME_COLORS["primary"],
            corner_radius=6,
            width=35
        )
        self.btn_stats.pack(side="left", padx=(4, 0))
        ToolTip(self.btn_stats, "Wyświetl statystyki i historię pobrań")


        # ═══════════════════════════════════════════════════════════════════
        # SEKCJA PRZYCISKÓW
        # ═══════════════════════════════════════════════════════════════════

        button_frame = CTkFrame(main_frame, fg_color="transparent")
        button_frame.pack(fill="x", pady=2)

        # ...existing code...
        # HASH_CONVERT_BTN: Główny przycisk konwersji
        self.btn_convert = CTkButton(
            button_frame,
            text="▶️ KONWERTUJ",
            command=self.start_conversion,
            height=26,
            font=("Helvetica", 12, "bold"),
            fg_color=THEME_COLORS["accent"],
            hover_color=THEME_COLORS["hover"],
            text_color=THEME_COLORS["text_primary"],
            corner_radius=6
        )
        self.btn_convert.pack(side="left", padx=2, fill="both", expand=True)
        ToolTip(self.btn_convert, "Rozpocznij pobieranie i konwersję do MP3")

        # Przycisk anulowania
        # HASH_CANCEL_BTN: Przycisk anulowania
        self.btn_cancel = CTkButton(
            button_frame,
            text="❌ Anuluj",
            command=self.cancel_conversion,
            height=26,
            font=("Helvetica", 12, "bold"),
            fg_color="#444444",
            hover_color="#555555",
            text_color=THEME_COLORS["text_primary"],
            corner_radius=6,
            state="disabled"
        )
        self.btn_cancel.pack(side="left", padx=2, fill="both", expand=True)
        ToolTip(self.btn_cancel, "Zatrzymaj bieżące pobieranie")

        # Przycisk wyczyść wyszukiwanie
        # HASH_CLEAR_SEARCH_BTN: Przycisk resetowania wyszukiwania
        self.btn_clear_search = CTkButton(
            button_frame,
            text="🔄 Wyczyść",
            command=self.clear_search,
            height=26,
            font=("Helvetica", 12, "bold"),
            fg_color="#555555",
            hover_color="#666666",
            text_color=THEME_COLORS["text_primary"],
            corner_radius=6
        )
        self.btn_clear_search.pack(side="left", padx=2, fill="both", expand=True)
        ToolTip(self.btn_clear_search, "Wyczyść formularz i zacznij od nowa")

        # Przycisk dźwięku
        # HASH_SOUND_BTN: Przycisk włączania dźwięku
        self.sound_enabled = self.app_config.get('sound_enabled', True)
        sound_text = "🔊 Dźwięk" if self.sound_enabled else "🔇 Cicho"
        self.btn_sound = CTkButton(
            button_frame,
            text=sound_text,
            command=self.toggle_sound,
            height=26,
            font=("Helvetica", 12, "bold"),
            fg_color="#555555",
            hover_color="#666666",
            text_color=THEME_COLORS["text_primary"],
            corner_radius=6
        )
        self.btn_sound.pack(side="left", padx=2, fill="both", expand=True)
        ToolTip(self.btn_sound, "Włącz/wyłącz powiadomienia dźwiękowe")

        # Podłącz callback zmiany jakości
        self.quality_selector.configure(command=self.update_quality_info)

    def update_quality_info(self, choice=None):
        """
        # KOMENTARZ PL: Aktualizuje info o przybliżonym rozmiarze pliku
        # HASH_QUALITY_INFO_UPDATE: Callback zmiany jakości
        """
        quality_map = {
            "128 kbps (Dobra - mały plik)": "≈ 1 MB/min",
            "192 kbps (Bardzo dobra)": "≈ 1.5 MB/min",
            "256 kbps (Wysoka)": "≈ 2 MB/min",
            "320 kbps (Najwyższa)": "≈ 3-4 MB/min"
        }

        selected = self.quality_var.get()
        size_info = quality_map.get(selected, "≈ 3-4 MB/min")
        self.quality_info.configure(text=size_info)
        logger.info(f"🎵 Wybrana jakość: {selected}")

    def get_selected_bitrate(self) -> str:
        """
        # KOMENTARZ PL: Zwraca wartość bitrate z wybranej opcji
        # HASH_BITRATE_PARSER: Ekstraktuje wartość kbps
        """
        selected = self.quality_var.get()
        # Wyciągnij liczbę z tekstu "320 kbps (Najwyższa)" -> "320"
        bitrate = selected.split()[0]
        return bitrate

    def toggle_sound(self):
        """
        # KOMENTARZ PL: Przełącza dźwięki powiadomień
        # HASH_TOGGLE_SOUND: Włącz/Wyłącz dźwięk
        """
        self.sound_enabled = not self.sound_enabled
        self.app_config.set('sound_enabled', self.sound_enabled)

        sound_text = "🔊 Dźwięk" if self.sound_enabled else "🔇 Cicho"
        self.btn_sound.configure(text=sound_text)

        logger.info(f"{'🔊 Dźwięk' if self.sound_enabled else '🔇 Cicho'} zmieniony")

        # Testowy dźwięk
        if self.sound_enabled:
            self.sound_manager.play_sound('start')

    def clear_search(self):
        """
        # KOMENTARZ PL: Wyczyści wyszukiwanie - resetuje URL i informacje
        # HASH_CLEAR_SEARCH: Reset wyszukiwania
        """
        # Wyczyść pole URL
        self.url_entry.delete(0, "end")
        self.last_url = ""

        # Resetuj informacje
        self.info_display.configure(
            text="📹 Wklej link YouTube\n⚡ Automatyczne sprawdzenie",
            text_color=THEME_COLORS["text_secondary"]
        )

        # Wyczyść miniaturę
        self.clear_thumbnail()

        # Resetuj statystyki
        self.progress_bar.set(0)
        self.progress_percent_label.configure(text="0%")
        self.progress_status_label.configure(text="Gotowy", text_color=THEME_COLORS["text_secondary"])
        self.progress_size_label.configure(text="0 MB")
        self.progress_speed_label.configure(text="0 MB/s")
        self.progress_eta_label.configure(text="--:--")

        # Resetuj zmienne
        self.is_playlist = False
        self.playlist_count = 0
        self.progress_start_time = 0
        self.progress_last_update = 0
        self.progress_downloaded = 0

        logger.info("🔄 Wyszukiwanie wyczyszczono - gotowy do nowego linku!")

    def on_url_change(self, event=None):
        """
        # KOMENTARZ PL: Auto-sprawdzanie URL po wpisaniu
        # HASH_AUTO_CHECK: Automatyczne pobieranie info
        """
        url = self.url_entry.get().strip()

        # Sprawdź czy URL się zmienił i zawiera youtube
        if url and url != self.last_url and ('youtube.com' in url or 'youtu.be' in url):
            self.last_url = url
            # Odczekaj 500ms i sprawdź (debounce)
            self.after(500, lambda: self._auto_check_url(url))

    def _auto_check_url(self, url):
        """
        # KOMENTARZ PL: Wewnętrzna metoda auto-sprawdzania
        """
        current_url = self.url_entry.get().strip()
        # Sprawdź czy URL nadal się zgadza (użytkownik mógł zmienić)
        if current_url == url:
            logger.info("⚡ Auto-sprawdzanie URL...")
            threading.Thread(target=self._check_info_thread, args=(url,), daemon=True).start()

    def load_thumbnail(self, thumbnail_url: str):
        """
        # KOMENTARZ PL: Pobiera i wyświetla miniaturę wideo
        # HASH_THUMBNAIL_LOADER: Ładowanie obrazka z URL
        """
        try:
            if not thumbnail_url:
                logger.warning("⚠️ Brak URL miniatury")
                return

            logger.info(f"🖼️ Pobieranie miniatury: {thumbnail_url[:100]}...")

            # Pobierz obrazek
            response = requests.get(thumbnail_url, timeout=10)
            response.raise_for_status()
            logger.info(f"✅ Miniatura pobrana, rozmiar: {len(response.content)} bajtów")

            # Otwórz jako PIL Image
            image = Image.open(BytesIO(response.content))
            logger.info(f"✅ Obraz otwarty: {image.size} px, format: {image.format}")

            # Zmień rozmiar do 105x95 (proporcjonalnie)
            image.thumbnail((105, 95), Image.Resampling.LANCZOS)
            logger.info(f"✅ Obraz przeskalowany do: {image.size}")

            # Konwertuj do CTkImage
            ctk_image = CTkImage(light_image=image, dark_image=image, size=(105, 95))

            # Wyświetl W GŁÓWNYM WĄTKU używając after()
            def update_ui():
                try:
                    # Resetuj stary obraz
                    self.thumbnail_label.configure(image=None)
                    # Ustaw nowy obraz
                    self.thumbnail_label.configure(image=ctk_image)
                    # Wyczyść tekst
                    self.thumbnail_label.configure(text="")
                    self.current_thumbnail = ctk_image  # Zachowaj referencję
                    logger.info("✅ Miniatura wyświetlona w UI")
                except Exception as ui_error:
                    logger.error(f"⚠️ Błąd wyświetlania miniatury: {str(ui_error)}")
                    self.thumbnail_label.configure(image=None, text="🎬", font=("Helvetica", 32))

            self.after(0, update_ui)

        except Exception as e:
            logger.error(f"❌ Błąd ładowania miniatury: {str(e)}", exc_info=True)

            def show_error():
                try:
                    self.thumbnail_label.configure(image=None, text="🎬", font=("Helvetica", 32))
                except:
                    pass

            self.after(0, show_error)

    def clear_thumbnail(self):
        """
        # KOMENTARZ PL: Czyści miniaturę - bezpiecznie obsługuje obrazy
        """
        try:
            # Bezpiecznie wyczyść obrazek
            self.thumbnail_label.configure(image=None)
            self.thumbnail_label.configure(text="🎬", font=("Helvetica", 32))
            self.current_thumbnail = None
        except Exception as e:
            logger.warning(f"⚠️ Nie można wyczyścić miniatury: {str(e)}")
            try:
                self.thumbnail_label.configure(text="🎬", font=("Helvetica", 32))
            except:
                pass

    def on_format_change(self, choice=None):
        """
        # KOMENTARZ PL: Callback zmiany formatu audio
        # HASH_FORMAT_CHANGE: Zapis wybranego formatu
        """
        format_full = self.format_var.get()
        # Wyciągnij skrót formatu z tekstu "MP3 (MPEG Audio)" -> "mp3"
        self.selected_format = format_full.split()[0].lower()
        logger.info(f"🎵 Wybrany format: {self.selected_format}")

    def show_statistics(self):
        """
        # KOMENTARZ PL: Wyświetla statystyki pobrań w stylu Matrix/Hacker
        # HASH_STATISTICS: Historia i analityka
        """
        stats = self.download_history.get_statistics()
        history = self.download_history.get_history(limit=10)

        # Stwórz okno statystyk - styl Matrix
        stats_window = ctk.CTkToplevel(self)
        stats_window.title("📊 Statystyki i Historia")
        stats_window.geometry("740x750")
        stats_window.resizable(False, False)
        stats_window.attributes('-topmost', True)  # Zawsze na wierzchu
        stats_window.attributes('-alpha', 0.96)    # Przezroczystość 96%

        # Wyśrodkuj okno
        stats_window.update_idletasks()
        x = (stats_window.winfo_screenwidth() // 2) - (740 // 2)
        y = (stats_window.winfo_screenheight() // 2) - (750 // 2)
        stats_window.geometry(f"740x750+{x}+{y}")

        # Główny kontener
        main_frame = CTkFrame(stats_window, fg_color=THEME_COLORS["primary"])
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Nagłówek - ikona i tytuł
        header_container = CTkFrame(main_frame, fg_color="transparent")
        header_container.pack(fill="x", pady=(0, 15))

        icon_label = CTkLabel(
            header_container,
            text="📊",
            font=("Helvetica", 32)
        )
        icon_label.pack(side="left", padx=(0, 10))

        title_container = CTkFrame(header_container, fg_color="transparent")
        title_container.pack(side="left", fill="both", expand=True)

        title_label = CTkLabel(
            title_container,
            text="Statystyki i Historia",
            font=("Helvetica", 16, "bold"),
            text_color=THEME_COLORS["text_primary"],
            anchor="w"
        )
        title_label.pack(anchor="w")

        subtitle_label = CTkLabel(
            title_container,
            text="Analityka pobrań i historia konwersji",
            font=("Helvetica", 9),
            text_color=THEME_COLORS["text_secondary"],
            anchor="w"
        )
        subtitle_label.pack(anchor="w")

        # Separator
        separator1 = CTkFrame(main_frame, height=1, fg_color="#3a3a3a")
        separator1.pack(fill="x", pady=(0, 15))

        # Statystyki - eleganckie ramki
        stats_frame = CTkFrame(main_frame, fg_color=THEME_COLORS["secondary"], corner_radius=8)
        stats_frame.pack(fill="x", pady=(0, 12))

        stats_title = CTkLabel(
            stats_frame,
            text="📈 Statystyki systemowe",
            font=("Helvetica", 11, "bold"),
            text_color=THEME_COLORS["text_primary"]
        )
        stats_title.pack(anchor="w", padx=15, pady=(12, 8))

        # Kontener dla statystyk - siatka
        stats_grid = CTkFrame(stats_frame, fg_color="transparent")
        stats_grid.pack(fill="x", padx=15, pady=(0, 12))

        total_size_gb = stats['total_size_mb'] / 1024 if stats['total_size_mb'] > 1024 else stats['total_size_mb']
        size_unit = "GB" if stats['total_size_mb'] > 1024 else "MB"

        # Statystyka 1 - Pobrane pliki
        stat1_frame = CTkFrame(stats_grid, fg_color=THEME_COLORS["bg_input"], corner_radius=6)
        stat1_frame.pack(side="left", fill="both", expand=True, padx=(0, 5))

        CTkLabel(
            stat1_frame,
            text="📥",
            font=("Helvetica", 20)
        ).pack(pady=(8, 0))

        CTkLabel(
            stat1_frame,
            text=str(stats['total_downloads']),
            font=("Helvetica", 18, "bold"),
            text_color=THEME_COLORS["accent"]
        ).pack()

        CTkLabel(
            stat1_frame,
            text="Pobranych plików",
            font=("Helvetica", 8),
            text_color=THEME_COLORS["text_secondary"]
        ).pack(pady=(0, 8))

        # Statystyka 2 - Rozmiar
        stat2_frame = CTkFrame(stats_grid, fg_color=THEME_COLORS["bg_input"], corner_radius=6)
        stat2_frame.pack(side="left", fill="both", expand=True, padx=(5, 5))

        CTkLabel(
            stat2_frame,
            text="💾",
            font=("Helvetica", 20)
        ).pack(pady=(8, 0))

        CTkLabel(
            stat2_frame,
            text=f"{total_size_gb:.1f} {size_unit}",
            font=("Helvetica", 18, "bold"),
            text_color=THEME_COLORS["accent"]
        ).pack()

        CTkLabel(
            stat2_frame,
            text="Użyte miejsce",
            font=("Helvetica", 8),
            text_color=THEME_COLORS["text_secondary"]
        ).pack(pady=(0, 8))

        # Statystyka 3 - Format
        stat3_frame = CTkFrame(stats_grid, fg_color=THEME_COLORS["bg_input"], corner_radius=6)
        stat3_frame.pack(side="left", fill="both", expand=True, padx=(5, 0))

        CTkLabel(
            stat3_frame,
            text="🎵",
            font=("Helvetica", 20)
        ).pack(pady=(8, 0))

        CTkLabel(
            stat3_frame,
            text=stats['favorite_format'].upper(),
            font=("Helvetica", 18, "bold"),
            text_color=THEME_COLORS["accent"]
        ).pack()

        CTkLabel(
            stat3_frame,
            text="Ulubiony format",
            font=("Helvetica", 8),
            text_color=THEME_COLORS["text_secondary"]
        ).pack(pady=(0, 8))

        # Separator
        separator2 = CTkFrame(main_frame, height=1, fg_color="#3a3a3a")
        separator2.pack(fill="x", pady=(0, 12))

        # Historia pobrań - elegancka lista
        history_frame = CTkFrame(main_frame, fg_color=THEME_COLORS["secondary"], corner_radius=8)
        history_frame.pack(fill="both", expand=True, pady=(0, 12))

        # Nagłówek historii
        history_header = CTkLabel(
            history_frame,
            text="🕐 Ostatnie pobrania",
            font=("Helvetica", 11, "bold"),
            text_color=THEME_COLORS["text_primary"]
        )
        history_header.pack(anchor="w", padx=15, pady=(12, 8))

        # Scrollable lista historii
        history_scroll = ctk.CTkScrollableFrame(
            history_frame,
            fg_color=THEME_COLORS["bg_input"],
            corner_radius=6,
            height=280
        )
        history_scroll.pack(fill="both", expand=True, padx=15, pady=(0, 12))

        if history:
            for idx, (title, date, format_t, size) in enumerate(history, 1):
                # Item frame - wszystko w jednej linii
                item_frame = CTkFrame(history_scroll, fg_color=THEME_COLORS["secondary"], corner_radius=6)
                item_frame.pack(fill="x", pady=2, padx=5)

                # Kontener - jedna linia z wszystkim
                line_frame = CTkFrame(item_frame, fg_color="transparent")
                line_frame.pack(fill="x", padx=10, pady=8)

                # Numer
                CTkLabel(
                    line_frame,
                    text=f"{idx}.",
                    font=("Helvetica", 12, "bold"),
                    text_color=THEME_COLORS["accent"],
                    width=25
                ).pack(side="left", padx=(0, 5))

                # Tytuł - zajmuje większość miejsca
                title_display = title[:40] + "..." if len(title) > 40 else title
                CTkLabel(
                    line_frame,
                    text=title_display,
                    font=("Helvetica", 12),
                    text_color=THEME_COLORS["text_primary"],
                    anchor="w"
                ).pack(side="left", fill="x", expand=True, padx=(0, 10))

                size_mb = size / (1024*1024) if size else 0

                # Format - kompaktowo
                CTkLabel(
                    line_frame,
                    text=format_t.upper(),
                    font=("Helvetica", 12, "bold"),
                    text_color=THEME_COLORS["accent"],
                    width=50
                ).pack(side="left", padx=(0, 10))

                # Rozmiar - kompaktowo
                CTkLabel(
                    line_frame,
                    text=f"{size_mb:.1f} MB",
                    font=("Helvetica", 12),
                    text_color=THEME_COLORS["text_secondary"],
                    width=70
                ).pack(side="left", padx=(0, 5))

                # Przycisk do otwarcia folderu
                def open_folder(folder=self.output_folder):
                    import os
                    import subprocess
                    if os.path.exists(folder):
                        subprocess.Popen(f'explorer "{os.path.normpath(folder)}"')

                folder_btn = CTkButton(
                    line_frame,
                    text="📁",
                    command=open_folder,
                    width=30,
                    height=24,
                    font=("Helvetica", 14),
                    fg_color=THEME_COLORS["bg_input"],
                    hover_color=THEME_COLORS["accent"],
                    corner_radius=4
                )
                folder_btn.pack(side="left")
        else:
            no_history_frame = CTkFrame(history_scroll, fg_color="transparent")
            no_history_frame.pack(fill="both", expand=True, pady=60)

            CTkLabel(
                no_history_frame,
                text="📭",
                font=("Helvetica", 40)
            ).pack(pady=(0, 10))

            CTkLabel(
                no_history_frame,
                text="Brak historii pobrań",
                font=("Helvetica", 12, "bold"),
                text_color=THEME_COLORS["text_secondary"]
            ).pack()

            CTkLabel(
                no_history_frame,
                text="Pobierz pierwsze pliki aby zobaczyć statystyki",
                font=("Helvetica", 9),
                text_color=THEME_COLORS["text_secondary"]
            ).pack(pady=(5, 0))

        # Przyciski na dole
        buttons_frame = CTkFrame(main_frame, fg_color="transparent")
        buttons_frame.pack(fill="x", pady=(0, 0))

        # Przycisk czyszczenia
        def clear_hist():
            if messagebox.askyesno("⚠️ Potwierdzenie", "Czy na pewno wyczyścić całą historię?"):
                self.download_history.clear_history()
                messagebox.showinfo("✅ Sukces", "Historia została wyczyszczona!")
                stats_window.destroy()

        btn_clear = CTkButton(
            buttons_frame,
            text="🗑️ Wyczyść historię",
            command=clear_hist,
            height=32,
            font=("Helvetica", 10, "bold"),
            fg_color=THEME_COLORS["secondary"],
            hover_color=THEME_COLORS["bg_input"],
            text_color=THEME_COLORS["text_primary"],
            corner_radius=6
        )
        btn_clear.pack(side="left", fill="both", expand=True, padx=(0, 5))

        # Przycisk zamknięcia
        btn_close = CTkButton(
            buttons_frame,
            text="✓ Zamknij",
            command=stats_window.destroy,
            height=32,
            font=("Helvetica", 10, "bold"),
            fg_color=THEME_COLORS["accent"],
            hover_color=THEME_COLORS["hover"],
            text_color=THEME_COLORS["text_primary"],
            corner_radius=6
        )
        btn_close.pack(side="left", fill="both", expand=True, padx=(5, 0))

        # Skróty klawiszowe
        stats_window.bind('<Escape>', lambda e: stats_window.destroy())
        stats_window.bind('<Return>', lambda e: stats_window.destroy())

    def show_about(self):
        """
        # KOMENTARZ PL: Wyświetla profesjonalne informacje o autorze w stylu GitHub
        # HASH_ABOUT: O autorze i programie
        """
        import webbrowser

        # Stwórz okno O autorze - większe dla ASCII art
        about_window = ctk.CTkToplevel(self)
        about_window.title("👤 O Programie i Autorze")
        about_window.geometry("740x740")
        about_window.resizable(False, False)
        about_window.attributes('-topmost', True)  # Zawsze na wierzchu
        about_window.attributes('-alpha', 0.96)    # Lekka przezroczystość

        # Wyśrodkuj okno
        about_window.update_idletasks()
        x = (about_window.winfo_screenwidth() // 2) - (740 // 2)
        y = (about_window.winfo_screenheight() // 2) - (740 // 2)
        about_window.geometry(f"740x740+{x}+{y}")

        # Główny kontener z możliwością scrollowania
        main_frame = CTkFrame(about_window, fg_color=THEME_COLORS["primary"])
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # ASCII Art Header w stylu GitHub
        ascii_art = """
╔════════════════════════════════════════════════════════════╗
║          🎵 YOUTUBE TO MP3 CONVERTER v2.0 🎵              ║
╚════════════════════════════════════════════════════════════╝

    ██╗   ██╗████████╗    ████████╗ ██████╗     ███╗   ███╗██████╗ ██████╗ 
    ╚██╗ ██╔╝╚══██╔══╝    ╚══██╔══╝██╔═══██╗    ████╗ ████║██╔══██╗╚════██╗
     ╚████╔╝    ██║          ██║   ██║   ██║    ██╔████╔██║██████╔╝ █████╔╝
      ╚██╔╝     ██║          ██║   ██║   ██║    ██║╚██╔╝██║██╔═══╝  ╚═══██╗
       ██║      ██║          ██║   ╚██████╔╝    ██║ ╚═╝ ██║██║     ██████╔╝
       ╚═╝      ╚═╝          ╚═╝    ╚═════╝     ╚═╝     ╚═╝╚═╝     ╚═════╝ 
"""

        ascii_label = CTkLabel(
            main_frame,
            text=ascii_art,
            font=("Courier New", 7),
            text_color="#00ff00",
            justify="left"
        )
        ascii_label.pack(pady=(0, 10))

        # Separator
        separator1 = CTkFrame(main_frame, height=2, fg_color=THEME_COLORS["accent"])
        separator1.pack(fill="x", pady=(0, 10))

        # Informacje o autorze w ramce
        author_frame = CTkFrame(main_frame, fg_color=THEME_COLORS["secondary"], corner_radius=8)
        author_frame.pack(fill="x", pady=(0, 10))

        author_info = """👨‍💻 AUTOR: Stanisław Kozioł
🌐 GitHub: github.com/crahdlinuxservers-maker
📧 Issues: github.com/crahdlinuxservers-maker/YouTubeToMP3/issues
💼 Role: Software Developer | Python Enthusiast"""

        author_label = CTkLabel(
            author_frame,
            text=author_info,
            font=("Courier New", 12),
            text_color=THEME_COLORS["text_primary"],
            justify="left"
        )
        author_label.pack(padx=15, pady=12, anchor="w")

        # Separator
        separator2 = CTkFrame(main_frame, height=1, fg_color="#3a3a3a")
        separator2.pack(fill="x", pady=(0, 10))

        # Opis projektu
        description_frame = CTkFrame(main_frame, fg_color=THEME_COLORS["secondary"], corner_radius=8)
        description_frame.pack(fill="x", pady=(0, 10))

        description = """📖 OPIS PROJEKTU:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Profesjonalny konwerter audio umożliwiający pobieranie
i konwersję materiałów z YouTube do formatów audio
(MP3, M4A, WAV, FLAC, OGG) z najwyższą jakością.

Program oferuje intuicyjny interfejs graficzny oparty
o CustomTkinter, zaawansowane opcje pobierania playlist,
automatyczne tagowanie ID3, historię pobrań oraz
wielowątkowe przetwarzanie dla maksymalnej wydajności."""

        desc_label = CTkLabel(
            description_frame,
            text=description,
            font=("Courier New", 12),
            text_color=THEME_COLORS["text_secondary"],
            justify="left"
        )
        desc_label.pack(padx=15, pady=10, anchor="w")

        # Kluczowe funkcje w stylu GitHub
        features_frame = CTkFrame(main_frame, fg_color=THEME_COLORS["secondary"], corner_radius=8)
        features_frame.pack(fill="x", pady=(0, 10))

        features_text = """⚡ KLUCZOWE FUNKCJE:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✓ Multi-format support  → MP3, M4A, WAV, FLAC, OGG
✓ Playlist handling     → Batch download & conversion
✓ ID3 Tagging          → Automatic metadata embedding
✓ Download history     → SQLite database tracking
✓ Multi-threading      → Parallel processing engine
✓ FFmpeg integration   → Professional audio encoding
✓ Quality presets      → 128-320 kbps bitrate options
✓ Dark theme UI        → Modern CustomTkinter interface"""

        features_label = CTkLabel(
            features_frame,
            text=features_text,
            font=("Courier New", 12),
            text_color=THEME_COLORS["text_secondary"],
            justify="left"
        )
        features_label.pack(padx=15, pady=10, anchor="w")

        # Technologie
        tech_frame = CTkFrame(main_frame, fg_color=THEME_COLORS["bg_input"], corner_radius=8)
        tech_frame.pack(fill="x", pady=(0, 10))

        tech_text = """🛠️  STACK TECHNOLOGICZNY:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• Python 3.14+     • CustomTkinter    • yt-dlp
• FFmpeg           • Mutagen (ID3)    • SQLite3
• Threading        • Pillow (PIL)     • Requests"""

        tech_label = CTkLabel(
            tech_frame,
            text=tech_text,
            font=("Courier New", 12),
            text_color=THEME_COLORS["text_primary"],
            justify="left"
        )
        tech_label.pack(padx=15, pady=8, anchor="w")

        # Linki - GitHub style buttons
        links_frame = CTkFrame(main_frame, fg_color="transparent")
        links_frame.pack(fill="x", pady=(0, 8))

        def open_github():
            webbrowser.open("https://github.com/crahdlinuxservers-maker/")

        def open_issues():
            webbrowser.open("https://github.com/crahdlinuxservers-maker/YouTubeToMP3/issues")

        def open_repo():
            webbrowser.open("https://github.com/crahdlinuxservers-maker/YouTubeToMP3")

        # 3 przyciski obok siebie
        btn_container = CTkFrame(links_frame, fg_color="transparent")
        btn_container.pack(fill="x")

        github_btn = CTkButton(
            btn_container,
            text="🌐 GitHub",
            command=open_github,
            height=32,
            font=("Helvetica", 12, "bold"),
            fg_color="#2ea44f",
            hover_color="#2c974b",
            text_color=THEME_COLORS["text_primary"],
            corner_radius=6
        )
        github_btn.pack(side="left", fill="both", expand=True, padx=(0, 3))

        repo_btn = CTkButton(
            btn_container,
            text="📦 Repository",
            command=open_repo,
            height=32,
            font=("Helvetica", 12, "bold"),
            fg_color="#0969da",
            hover_color="#0860ca",
            text_color=THEME_COLORS["text_primary"],
            corner_radius=6
        )
        repo_btn.pack(side="left", fill="both", expand=True, padx=(3, 3))

        issues_btn = CTkButton(
            btn_container,
            text="🐛 Issues",
            command=open_issues,
            height=32,
            font=("Helvetica", 12, "bold"),
            fg_color="#6e7681",
            hover_color="#8c959f",
            text_color=THEME_COLORS["text_primary"],
            corner_radius=6
        )
        issues_btn.pack(side="left", fill="both", expand=True, padx=(3, 0))

        # Footer z licencją
        footer_frame = CTkFrame(main_frame, fg_color="transparent")
        footer_frame.pack(fill="x", pady=(8, 0))

        footer_text = "MIT License © 2026 | Made with ❤️ in Python"
        footer_label = CTkLabel(
            footer_frame,
            text=footer_text,
            font=("Courier New", 12),
            text_color="#666666"
        )
        footer_label.pack()

        # Przycisk zamknięcia na dole
        close_btn = CTkButton(
            main_frame,
            text="✓ Zamknij",
            command=about_window.destroy,
            height=32,
            font=("Helvetica", 12, "bold"),
            fg_color=THEME_COLORS["accent"],
            hover_color=THEME_COLORS["hover"],
            text_color=THEME_COLORS["text_primary"],
            corner_radius=6
        )
        close_btn.pack(fill="x", pady=(10, 0))

        # Skróty klawiszowe
        about_window.bind('<Escape>', lambda e: about_window.destroy())
        about_window.bind('<Return>', lambda e: about_window.destroy())

    def select_folder(self):
        """
        # KOMENTARZ PL: Otwiera dialog wyboru folderu
        # HASH_FOLDER_SELECTION: Obsługa wyboru folderu
        """
        folder = filedialog.askdirectory(title="Wybierz folder docelowy")
        if folder:
            self.output_folder = folder
            self.folder_display.configure(text=folder)
            # Zapamiętaj ostatni folder
            self.app_config.set('last_folder', folder)
            logger.info(f"📁 Wybrany folder: {folder} (zapisany)")


    def check_video_info(self):
        """
        # KOMENTARZ PL: Pobiera i wyświetla informacje o wideo
        # HASH_VIDEO_INFO_FETCH: Pobieranie metadanych
        """
        url = self.url_entry.get().strip()

        if not url:
            messagebox.showerror("❌ Błąd", "Wklej link YouTube!")
            return

        # Resetuj miniaturę bezpiecznie
        try:
            self.thumbnail_label.configure(image=None)
            self.thumbnail_label.configure(text="🎬", font=("Helvetica", 32))
            self.current_thumbnail = None
        except:
            pass

        # Pokaż status
        self.info_display.configure(
            text="⏳ Pobieranie informacji...",
            text_color=THEME_COLORS["warning"]
        )
        self.update()

        # Pobierz w oddzielnym wątku
        # HASH_THREADING_INFO: Asynchroniczne pobieranie info
        thread = threading.Thread(target=self._fetch_info_thread, args=(url,))
        thread.daemon = True
        thread.start()

    def _check_info_thread(self, url):
        """
        # KOMENTARZ PL: Wątek do pobierania informacji (uniwersalny)
        # HASH_CHECK_INFO_THREAD: Pobieranie metadanych z miniaturą
        """
        try:
            logger.info(f"🧵 Wątek: Rozpoczęto pobieranie info dla: {url}")

            # Wyczyść miniaturę
            self.clear_thumbnail()

            converter = YouTubeToMP3Converter(self.output_folder)
            info = converter.get_video_info(url)
            logger.info(f"🧵 Wątek: Odpowiedź: {info}")

            if info.get('valid'):
                self.is_playlist = info.get('is_playlist', False)
                self.playlist_count = info.get('playlist_count', 0)

                if self.is_playlist:
                    # To jest playlista
                    info_text = f"📋 PLAYLISTA\n\n🎯 {info['title'][:30]}\n📊 {self.playlist_count} wideo\n\n✅ Checkbox = Pobierz wszystkie"
                    logger.info(f"📋 Playlista: {info['title']} ({self.playlist_count} wideo)")
                else:
                    # To jest pojedyncze wideo
                    duration_min = info['duration'] // 60
                    duration_sec = info['duration'] % 60
                    title = info['title'][:35]  # Skróć długi tytuł
                    channel = info['channel'][:28]  # Skróć kanał
                    info_text = f"📹 {title}\n🎤 {channel}\n⏱️ {duration_min}:{duration_sec:02d}"

                    # Pobierz miniaturę (load_thumbnail już używa after() dla UI)
                    thumbnail_url = info.get('thumbnail')
                    if thumbnail_url:
                        logger.info(f"🧵 Uruchamiam ładowanie miniatury: {thumbnail_url[:50]}...")
                        self.load_thumbnail(thumbnail_url)
                    else:
                        logger.warning("⚠️ Brak URL miniatury w odpowiedzi")

                    logger.info(f"✅ Wideo: {info['title']}")

                self.info_display.configure(
                    text=info_text,
                    text_color=THEME_COLORS["success"]
                )
                self.update()
            else:
                error_msg = info.get('error', 'Nieznany błąd')
                self.info_display.configure(
                    text=f"❌ BŁĄD\n\n{error_msg[:40]}",
                    text_color="#ff6b6b"
                )
                self.update()
                logger.error(f"❌ Błąd: {error_msg}")

        except Exception as e:
            error_text = str(e)
            logger.error(f"🧵 Wyjątek: {error_text}", exc_info=True)
            self.info_display.configure(
                text=f"❌ Błąd: {error_text}",
                text_color="#ff6b6b"
            )
            self.update()

    def _fetch_info_thread(self, url):
        """
        # KOMENTARZ PL: Stara nazwa - przekierowanie do _check_info_thread
        """
        self._check_info_thread(url)

    def show_playlist_selector(self, url):
        """
        # KOMENTARZ PL: Wyświetla okno do wyboru wideo z playlisty
        # HASH_PLAYLIST_SELECTOR: Wybór wideo z playlisty z LIVE ładowaniem
        """
        logger.info(f"🎬 show_playlist_selector uruchomiony dla: {url[:50]}...")

        # OTWÓRZ OKNO OD RAZU (przed pobraniem danych) - styl jak "O autorze"
        selector_window = ctk.CTkToplevel(self)
        selector_window.title(f"📋 Ładowanie playlisty...")
        selector_window.geometry("900x750")
        selector_window.resizable(False, False)
        selector_window.attributes('-topmost', True)  # Zawsze na wierzchu
        selector_window.attributes('-alpha', 0.96)    # Przezroczystość 96%

        # Wyśrodkuj okno
        selector_window.update_idletasks()
        x = (selector_window.winfo_screenwidth() // 2) - (900 // 2)
        y = (selector_window.winfo_screenheight() // 2) - (750 // 2)
        selector_window.geometry(f"900x750+{x}+{y}")

        selector_window.transient(self)
        selector_window.grab_set()

        # Frame główny z efektem Matrix
        main_container = CTkFrame(selector_window, fg_color=THEME_COLORS["primary"])
        main_container.pack(fill="both", expand=True)

        # ASCII Art Matrix Header
        matrix_art = """
    ███╗   ███╗ █████╗ ████████╗██████╗ ██╗██╗  ██╗
    ████╗ ████║██╔══██╗╚══██╔══╝██╔══██╗██║╚██╗██╔╝
    ██╔████╔██║███████║   ██║   ██████╔╝██║ ╚███╔╝ 
    ██║╚██╔╝██║██╔══██║   ██║   ██╔══██╗██║ ██╔██╗ 
    ██║ ╚═╝ ██║██║  ██║   ██║   ██║  ██║██║██╔╝ ██╗
    ╚═╝     ╚═╝╚═╝  ╚═╝   ╚═╝   ╚═╝  ╚═╝╚═╝╚═╝  ╚═╝
        [ PLAYLIST EXTRACTOR v3.14 - NEURAL MODE ]
"""

        matrix_label = CTkLabel(
            main_container,
            text=matrix_art,
            font=("Courier New", 8, "bold"),
            text_color="#00ff00",
            justify="left"
        )
        matrix_label.pack(pady=(10, 5), padx=10)

        # Nagłówek - hakerski styl
        header = CTkLabel(
            main_container,
            text="📋 >>> INITIALIZING QUANTUM DECODER <<<",
            font=("Courier New", 16, "bold"),
            text_color="#00ff00"
        )
        header.pack(pady=(5, 15), padx=10)

        # Terminal (scrollable) - tutaj będą ładować się wideo - większy
        terminal_frame = ctk.CTkScrollableFrame(
            main_container,
            fg_color="#0a0a0a",
            corner_radius=8,
            height=420
        )
        terminal_frame.pack(fill="both", expand=True, padx=20, pady=(0, 15))

        # Label dla terminala - większa czcionka z efektami
        terminal_output = CTkLabel(
            terminal_frame,
            text=""">>> [SYSTEM] Booting neural network...
>>> [MATRIX] Loading encryption keys...
>>> [CORE] Initializing quantum processors...
>>> [NET] Establishing secure tunnel...
>>> [STATUS] All systems GREEN ✓
>>> [READY] Awaiting target coordinates...""",
            font=("Courier New", 10),
            text_color="#00ff00",
            fg_color="transparent",
            justify="left",
            anchor="nw"
        )
        terminal_output.pack(fill="both", expand=True, padx=5, pady=5)

        # Pasek postępu - większy
        progress_bar = CTkProgressBar(
            main_container,
            height=20,
            fg_color=THEME_COLORS["bg_input"],
            progress_color="#00ff00"
        )
        progress_bar.pack(fill="x", padx=20, pady=(0, 12))
        progress_bar.set(0)

        # Status - większa czcionka
        status_label = CTkLabel(
            main_container,
            text="⚡ [SYSTEM] Connecting to YouTube API...",
            font=("Courier New", 11, "bold"),
            text_color="#ffff00"
        )
        status_label.pack(pady=(0, 12))

        # Przycisk Anuluj - większy i bardziej wyrazisty
        button_frame = CTkFrame(main_container, fg_color="transparent")
        button_frame.pack(fill="x", padx=20, pady=(0, 15))

        cancel_btn = CTkButton(
            button_frame,
            text="[ ESC ] ABORT MISSION",
            command=lambda: selector_window.destroy(),
            height=35,
            font=("Courier New", 11, "bold"),
            fg_color="#661111",
            hover_color="#882222",
            text_color="#ff4444"
        )
        cancel_btn.pack(fill="x")

        # Skrót ESC
        selector_window.bind('<Escape>', lambda e: selector_window.destroy())

        # Zmienne współdzielone
        shared_data = {
            'entries': [],
            'playlist_info': None,
            'loading_complete': False,
            'error': None
        }

        # Funkcja do dodawania linii do terminala - większy bufor
        terminal_lines = []
        def add_terminal_line(line):
            terminal_lines.append(line)
            if len(terminal_lines) > 50:  # Zwiększony bufor z 30 do 50
                terminal_lines.pop(0)
            selector_window.after(0, lambda: terminal_output.configure(text="\n".join(terminal_lines)))

        # Wątek ładowania w tle - hakerski styl Matrix
        def loading_thread():
            try:
                import time
                from yt_dlp import YoutubeDL

                add_terminal_line("╔════════════════════════════════════════════════╗")
                add_terminal_line("║  MATRIX PROTOCOL v3.14 - PLAYLIST EXTRACTION  ║")
                add_terminal_line("╚════════════════════════════════════════════════╝")
                add_terminal_line("")
                add_terminal_line(">>> [INIT] Booting AI neural network...")
                add_terminal_line(">>> [CPU] Allocating 512MB memory buffer...")
                add_terminal_line(">>> [GPU] Activating parallel processing cores...")
                time.sleep(0.2)

                add_terminal_line(">>> [NET] Establishing encrypted connection...")
                add_terminal_line(">>> [SSL] Generating RSA-4096 keys...")
                add_terminal_line(">>> [SSL] Handshake: SUCCESS ✓")
                selector_window.after(0, lambda: progress_bar.set(0.1))
                time.sleep(0.3)

                add_terminal_line(">>> [AUTH] Requesting API access token...")
                add_terminal_line(">>> [AUTH] Token received: ████████████████ ✓")
                add_terminal_line(">>> [AUTH] YouTube API: AUTHORIZED ✓")
                add_terminal_line("")
                add_terminal_line(f">>> [TARGET] URL acquired")
                add_terminal_line(f">>> [SCAN] {url[:65]}...")
                add_terminal_line(">>> [DECODE] Parsing URL structure...")
                add_terminal_line(">>> [STATUS] Initiating data extraction sequence...")
                selector_window.after(0, lambda: progress_bar.set(0.2))
                selector_window.after(0, lambda: status_label.configure(text="🔍 [PARSER] Decoding quantum data stream..."))
                time.sleep(0.3)

                # Pobierz listę
                ydl_opts = {
                    'quiet': True,
                    'no_warnings': True,
                    'extract_flat': 'in_playlist',
                }

                add_terminal_line("")
                add_terminal_line(">>> [EXTRACT] Downloading playlist metadata...")
                add_terminal_line(">>> [STREAM] Opening data channel...")
                add_terminal_line(">>> [BUFFER] Receiving packet stream...")
                add_terminal_line(">>> [PARSE] Decrypting JSON payload...")
                selector_window.after(0, lambda: progress_bar.set(0.3))
                time.sleep(0.2)

                with YoutubeDL(ydl_opts) as ydl:
                    add_terminal_line(">>> [DL] yt-dlp engine: ACTIVE ✓")
                    playlist_info = ydl.extract_info(url, download=False)
                    add_terminal_line(">>> [DL] Data extraction: COMPLETE ✓")

                selector_window.after(0, lambda: progress_bar.set(0.5))
                add_terminal_line("")
                add_terminal_line(">>> [VERIFY] Validating playlist format...")

                # Sprawdź czy to playlista
                if playlist_info.get('_type') != 'playlist':
                    entries = playlist_info.get('entries', [])
                    if not entries or len(entries) < 1:
                        add_terminal_line(">>> [ERROR] ⚠️  Invalid playlist structure!")
                        add_terminal_line(">>> [ERROR] Expected: playlist | Received: single video")
                        add_terminal_line(">>> [ABORT] Mission terminated with code 404")
                        add_terminal_line(">>> [EXIT] Closing connection...")
                        selector_window.after(0, lambda: status_label.configure(text="❌ [FATAL] Not a valid playlist!", text_color="#ff0000"))
                        time.sleep(2)
                        selector_window.after(0, lambda: selector_window.destroy())
                        return
                else:
                    entries = playlist_info.get('entries', [])

                if not entries:
                    add_terminal_line(">>> [ERROR] ⚠️  Playlist buffer is empty!")
                    add_terminal_line(">>> [ERROR] 0 entries found in data stream")
                    add_terminal_line(">>> [ABORT] Cannot proceed with empty dataset")
                    add_terminal_line(">>> [EXIT] Terminating connection...")
                    selector_window.after(0, lambda: status_label.configure(text="❌ [FATAL] Zero entries detected!", text_color="#ff0000"))
                    time.sleep(2)
                    selector_window.after(0, lambda: selector_window.destroy())
                    return

                total_videos = len(entries)
                add_terminal_line("")
                add_terminal_line("╔════════════════════════════════════════════════╗")
                add_terminal_line(f"║  ✓ EXTRACTION SUCCESSFUL - {total_videos} ENTRIES FOUND  ║")
                add_terminal_line("╚════════════════════════════════════════════════╝")
                add_terminal_line("")
                add_terminal_line(f">>> [DATA] Total video count: {total_videos}")
                add_terminal_line(f">>> [META] Playlist title: {playlist_info.get('title', 'Unknown')[:45]}")
                add_terminal_line(f">>> [META] Author: {playlist_info.get('uploader', 'Unknown')[:30]}")
                add_terminal_line(">>> [CACHE] Building binary index tree...")
                add_terminal_line(f">>> [MEMORY] Allocating {total_videos * 2}MB RAM...")
                selector_window.after(0, lambda t=total_videos: header.configure(text=f"📋 >>> {playlist_info.get('title', 'PLAYLIST')[:35]} <<<"))
                selector_window.after(0, lambda: progress_bar.set(0.6))
                selector_window.after(0, lambda t=total_videos: status_label.configure(text=f"✅ [SUCCESS] {t} videos decoded successfully!", text_color="#00ff00"))
                time.sleep(0.3)

                # Ładuj wideo z animacją hakerską Matrix
                add_terminal_line("")
                add_terminal_line(">>> [RENDER] Compiling video matrix...")
                add_terminal_line(">>> [GPU] Rendering visual interface...")
                add_terminal_line(">>> [DISPLAY] Generating playlist grid...")
                selector_window.after(0, lambda: progress_bar.set(0.7))
                time.sleep(0.2)

                # Pokazuj pierwsze kilka wideo z efektem Matrix
                add_terminal_line("")
                add_terminal_line("    ╔══════════════ VIDEO INDEX ══════════════╗")
                for i in range(min(12, total_videos)):
                    entry = entries[i]
                    title = entry.get('title', f'Video {i+1}')
                    duration = entry.get('duration', 0)
                    # Konwertuj duration na int (może być float z API)
                    if duration:
                        duration = int(duration)
                        dur_str = f"{duration//60}:{duration%60:02d}"
                    else:
                        dur_str = "LIVE"
                    add_terminal_line(f"    ║ [{i+1:03d}] {title[:45]:<45} │ {dur_str}")
                    time.sleep(0.04)  # Szybka animacja Matrix

                if total_videos > 12:
                    add_terminal_line(f"    ║ ... {total_videos - 12} more entries in database")
                add_terminal_line("    ╚══════════════════════════════════════════════╝")
                add_terminal_line("")

                selector_window.after(0, lambda: progress_bar.set(0.9))
                add_terminal_line(">>> [AI] Neural network analysis: COMPLETE ✓")
                add_terminal_line(">>> [BUILD] Compiling interactive GUI components...")
                add_terminal_line(">>> [THREAD] Spawning UI render process...")
                add_terminal_line(">>> [MATRIX] Initializing selection interface...")
                time.sleep(0.3)

                # Zapisz dane
                shared_data['entries'] = entries
                shared_data['playlist_info'] = playlist_info
                shared_data['loading_complete'] = True

                add_terminal_line("")
                add_terminal_line("╔════════════════════════════════════════════════╗")
                add_terminal_line("║     ✓✓✓ MISSION ACCOMPLISHED ✓✓✓              ║")
                add_terminal_line("║  All systems operational - Standing by...     ║")
                add_terminal_line("╚════════════════════════════════════════════════╝")
                add_terminal_line("")
                add_terminal_line(">>> [STATUS] Ready for user interaction ⚡")
                add_terminal_line(">>> [AWAIT] Select videos to download...")
                time.sleep(0.2)

                # PRZEKSZTAŁĆ OKNO W SELEKTOR
                selector_window.after(0, lambda: self.transform_to_selector(
                    selector_window,
                    main_container,
                    entries,
                    playlist_info,
                    url
                ))

            except Exception as e:
                logger.error(f"❌ Błąd ładowania: {str(e)}")
                add_terminal_line("")
                add_terminal_line("╔════════════════════════════════════════════════╗")
                add_terminal_line("║  ⚠️  CRITICAL SYSTEM ERROR DETECTED  ⚠️        ║")
                add_terminal_line("╚════════════════════════════════════════════════╝")
                add_terminal_line(f">>> [ERROR] Exception: {str(e)[:50]}")
                add_terminal_line(f">>> [TRACE] Stack trace logged to system")
                add_terminal_line(f">>> [FAIL] Mission aborted - Code 500")
                add_terminal_line(f">>> [EXIT] Shutting down neural network...")
                selector_window.after(0, lambda: status_label.configure(text=f"❌ [FATAL] Critical failure!", text_color="#ff0000"))
                selector_window.after(0, lambda: progress_bar.set(0))
                time.sleep(2.5)
                selector_window.after(0, lambda: selector_window.destroy())

        # Uruchom wątek
        thread = threading.Thread(target=loading_thread, daemon=True)
        thread.start()

    def transform_to_selector(self, selector_window, main_container, entries, playlist_info, url):
        """
        # KOMENTARZ PL: Przekształca okno ładowania w pełny selektor playlisty
        """
        # Wyczyść kontener
        for widget in main_container.winfo_children():
            widget.destroy()

        # Nagłówek
        header = CTkLabel(
            main_container,
            text=f"📋 {playlist_info.get('title', 'Playlista')}",
            font=("Helvetica", 14, "bold"),
            text_color=THEME_COLORS["text_primary"]
        )
        header.pack(pady=10, padx=10)

        subtitle = CTkLabel(
            main_container,
            text=f"Wybierz wideo do pobrania ({len(entries)} dostępnych)",
            font=("Helvetica", 12),
            text_color=THEME_COLORS["text_secondary"]
        )
        subtitle.pack(pady=(0, 10))

        # ===== PRZYCISKI ZAZNACZANIA =====
        select_frame = CTkFrame(main_container, fg_color="transparent")
        select_frame.pack(fill="x", padx=10, pady=(0, 10))

        # ===== PAGINACJA =====
        ITEMS_PER_PAGE = 50
        total_videos = len(entries)
        total_pages = (total_videos + ITEMS_PER_PAGE - 1) // ITEMS_PER_PAGE
        current_page = [0]

        checkbox_vars = []
        all_selected_videos = {}

        # Frame dla stron
        page_frame = CTkFrame(main_container, fg_color="transparent")
        page_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Info o stronie
        page_info_label = CTkLabel(
            page_frame,
            text=f"Strona 1 z {total_pages} ({total_videos} wideo)",
            font=("Helvetica", 9),
            text_color=THEME_COLORS["text_secondary"]
        )
        page_info_label.pack(pady=(0, 5))

        # ScrollableFrame dla wideo
        scroll_frame = ctk.CTkScrollableFrame(
            page_frame,
            fg_color=THEME_COLORS["secondary"],
            corner_radius=8,
            height=350
        )
        scroll_frame.pack(fill="both", expand=True, pady=(0, 10))

        def render_page(page_idx):
            """Renderuje wideo dla danej strony"""
            for widget in scroll_frame.winfo_children():
                widget.destroy()

            checkbox_vars.clear()

            start_idx = page_idx * ITEMS_PER_PAGE
            end_idx = min(start_idx + ITEMS_PER_PAGE, total_videos)

            logger.info(f"📄 Renderowanie strona {page_idx + 1}: wideo {start_idx + 1} do {end_idx}")

            for i in range(start_idx, end_idx):
                entry = entries[i]
                if not entry:
                    continue

                try:
                    title = entry.get('title', f'Video {i + 1}')
                    if not title:
                        title = f'Video {i + 1}'

                    duration = entry.get('duration', 0)
                    if duration is None:
                        duration = 0

                    try:
                        duration = int(duration)
                    except (ValueError, TypeError):
                        duration = 0

                    # Frame dla wideo
                    video_frame = CTkFrame(scroll_frame, fg_color=THEME_COLORS["bg_input"], corner_radius=4)
                    video_frame.pack(fill="x", pady=2, padx=3, expand=False)

                    # Sprawdź czy było zaznaczone
                    is_checked = all_selected_videos.get(i, {}).get('checked', False)

                    var = ctk.BooleanVar(value=is_checked)
                    checkbox_vars.append((i, var))

                    if duration and duration > 0:
                        duration_str = f"{duration // 60}:{duration % 60:02d}"
                    else:
                        duration_str = "?"

                    checkbox_text = f"{i + 1}. {title[:40]}{'...' if len(title) > 40 else ''} ({duration_str})"

                    def save_checkbox_state(idx=i, v=var):
                        all_selected_videos[idx]['checked'] = v.get()

                    checkbox = ctk.CTkCheckBox(
                        video_frame,
                        text=checkbox_text,
                        variable=var,
                        command=lambda idx=i, v=var: save_checkbox_state(idx, v),
                        font=("Helvetica", 12),
                        fg_color=THEME_COLORS["accent"],
                        hover_color=THEME_COLORS["hover"],
                        text_color=THEME_COLORS["text_secondary"],
                        checkbox_width=14,
                        checkbox_height=14
                    )
                    checkbox.pack(anchor="w", padx=6, pady=4)

                    # Zapisz dane wideo
                    if i not in all_selected_videos:
                        video_url = entry.get('url')
                        video_id = entry.get('id', '')

                        if not video_url:
                            if video_id:
                                video_url = f"https://www.youtube.com/watch?v={video_id}"
                            elif entry.get('webpage_url'):
                                video_url = entry.get('webpage_url')
                            else:
                                logger.warning(f"⚠️ Brak URL dla wideo {i}: {title}")
                                video_url = ""

                        all_selected_videos[i] = {
                            'var': var,
                            'entry': entry,
                            'title': title,
                            'url': video_url,
                            'checked': is_checked
                        }

                except Exception as e:
                    logger.error(f"⚠️ Błąd dodawania wideo {i}: {str(e)}")
                    continue

            page_info_label.configure(
                text=f"Strona {page_idx + 1} z {total_pages} (Wideo {start_idx + 1}-{end_idx} z {total_videos})"
            )

        # Renderuj pierwszą stronę
        render_page(0)

        # Nawigacja
        nav_frame = CTkFrame(main_container, fg_color="transparent")
        nav_frame.pack(fill="x", padx=10, pady=5)

        def update_nav_buttons():
            if current_page[0] == 0:
                btn_prev.configure(state="disabled")
            else:
                btn_prev.configure(state="normal")

            if current_page[0] >= total_pages - 1:
                btn_next.configure(state="disabled")
            else:
                btn_next.configure(state="normal")

            page_counter.configure(text=f"{current_page[0] + 1} / {total_pages}")

        def prev_page_updated():
            if current_page[0] > 0:
                current_page[0] -= 1
                render_page(current_page[0])
                update_nav_buttons()

        def next_page_updated():
            if current_page[0] < total_pages - 1:
                current_page[0] += 1
                render_page(current_page[0])
                update_nav_buttons()

        btn_prev = CTkButton(
            nav_frame,
            text="⬅️ Poprzednia",
            command=prev_page_updated,
            height=26,
            font=("Helvetica", 12, "bold"),
            fg_color="#555555",
            hover_color="#666666"
        )
        btn_prev.pack(side="left", padx=5, expand=True, fill="x")

        page_counter = CTkLabel(
            nav_frame,
            text=f"1 / {total_pages}",
            font=("Helvetica", 9, "bold"),
            text_color=THEME_COLORS["text_primary"]
        )
        page_counter.pack(side="left", padx=10)

        btn_next = CTkButton(
            nav_frame,
            text="Następna ➡️",
            command=next_page_updated,
            height=26,
            font=("Helvetica", 12, "bold"),
            fg_color="#555555",
            hover_color="#666666"
        )
        btn_next.pack(side="left", padx=5, expand=True, fill="x")

        update_nav_buttons()

        # Przyciski zaznaczania
        def select_all():
            for idx, var in checkbox_vars:
                var.set(True)
                if idx in all_selected_videos:
                    all_selected_videos[idx]['checked'] = True
            logger.info(f"✅ Zaznaczono wszystkie wideo na stronie {current_page[0] + 1}")

        def deselect_all():
            for idx, var in checkbox_vars:
                var.set(False)
                if idx in all_selected_videos:
                    all_selected_videos[idx]['checked'] = False
            logger.info(f"❌ Odznaczono wszystkie wideo na stronie {current_page[0] + 1}")

        btn_select_all = CTkButton(
            select_frame,
            text="✅ Zaznacz na tej stronie",
            command=select_all,
            height=28,
            font=("Helvetica", 12, "bold"),
            fg_color="#2d5016",
            hover_color="#3d6020",
            width=150
        )
        btn_select_all.pack(side="left", padx=5, expand=True, fill="x")
        ToolTip(btn_select_all, "Zaznacz wszystkie wideo na aktualnie widocznej stronie")

        btn_deselect_all = CTkButton(
            select_frame,
            text="❌ Odznacz na tej stronie",
            command=deselect_all,
            height=28,
            font=("Helvetica", 12, "bold"),
            fg_color="#501616",
            hover_color="#602020",
            width=150
        )
        btn_deselect_all.pack(side="left", padx=5, expand=True, fill="x")
        ToolTip(btn_deselect_all, "Odznacz wszystkie wideo na aktualnie widocznej stronie")

        # Przyciski OK/Anuluj
        button_frame = CTkFrame(main_container, fg_color="transparent")
        button_frame.pack(fill="x", padx=10, pady=10)

        def confirm():
            for idx, var in checkbox_vars:
                if idx in all_selected_videos:
                    all_selected_videos[idx]['checked'] = var.get()

            result_selected = [v for idx, v in all_selected_videos.items() if v.get('checked', False)]
            logger.info(f"✅ Potwierdzono wybór {len(result_selected)} wideo")

            selector_window.destroy()

            if result_selected:
                self.show_playlist_download_progress(result_selected)

        def cancel():
            selector_window.destroy()

        btn_ok = CTkButton(
            button_frame,
            text=f"▶️ Pobierz zaznaczone",
            command=confirm,
            height=32,
            font=("Helvetica", 12, "bold"),
            fg_color=THEME_COLORS["accent"],
            hover_color=THEME_COLORS["hover"],
            width=200
        )
        btn_ok.pack(side="left", padx=5, expand=True)

        btn_cancel = CTkButton(
            button_frame,
            text="❌ Anuluj",
            command=cancel,
            height=32,
            font=("Helvetica", 12, "bold"),
            fg_color="#555555",
            hover_color="#666666",
            width=120
        )
        btn_cancel.pack(side="left", padx=5)

    def show_playlist_download_progress(self, selected_videos):
        """
        # KOMENTARZ PL: Okno postępu pobierania playlisty - ULEPSZONA WERSJA
        # HASH_PLAYLIST_DOWNLOAD_PROGRESS: Dedykowane okno z mini paskami LIVE dla każdego pliku
        """
        logger.info(f"🎬 Otwieranie okna postępu pobierania dla {len(selected_videos)} wideo")

        # Stwórz okno postępu
        progress_window = ctk.CTkToplevel(self)
        progress_window.title(f"📥 Pobieranie playlisty ({len(selected_videos)} wideo)")
        progress_window.geometry("800x700")
        progress_window.resizable(False, False)

        # Wycentruj okno
        progress_window.transient(self)
        progress_window.grab_set()

        # Główny frame
        main_frame = CTkFrame(progress_window, fg_color=THEME_COLORS["primary"])
        main_frame.pack(fill="both", expand=True, padx=15, pady=15)

        # Nagłówek - powiększony
        header_label = CTkLabel(
            main_frame,
            text=f"📥 Pobieranie {len(selected_videos)} wideo z playlisty",
            font=("Helvetica", 16, "bold"),
            text_color=THEME_COLORS["accent"]
        )
        header_label.pack(pady=(5, 10))

        # Frame z listą wideo (scrollable)
        list_frame_container = CTkFrame(main_frame, fg_color=THEME_COLORS["secondary"], corner_radius=8)
        list_frame_container.pack(fill="both", expand=True, pady=(0, 10))

        list_label = CTkLabel(
            list_frame_container,
            text="📋 Zaznaczone wideo:",
            font=("Helvetica", 12, "bold"),
            text_color=THEME_COLORS["text_primary"]
        )
        list_label.pack(anchor="w", padx=10, pady=(8, 4))

        list_scroll = ctk.CTkScrollableFrame(
            list_frame_container,
            fg_color=THEME_COLORS["bg_input"],
            corner_radius=6,
            height=200
        )
        list_scroll.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        # Słowniki do przechowywania mini pasków i statystyk
        mini_progress_bars = {}
        mini_stats_labels = {}

        # Dodaj wideo do listy - WSZYSTKO W JEDNEJ LINII!
        for idx, video in enumerate(selected_videos, 1):
            video_frame = CTkFrame(list_scroll, fg_color=THEME_COLORS["secondary"], corner_radius=4)
            video_frame.pack(fill="x", pady=2, padx=2)

            # Jedna linia: tytuł | statystyki | pasek
            one_line_container = CTkFrame(video_frame, fg_color="transparent")
            one_line_container.pack(fill="x", padx=6, pady=4)

            # 1. Tytuł (po lewej)
            title = video.get('title', f'Video {idx}')
            video_label = CTkLabel(
                one_line_container,
                text=f"{idx}. {title[:28]}{'...' if len(title) > 28 else ''}",
                font=("Helvetica", 12),
                text_color=THEME_COLORS["text_secondary"],
                anchor="w",
                width=280
            )
            video_label.pack(side="left", padx=(0, 5))

            # 2. Statystyki LIVE (środek)
            mini_stats = CTkLabel(
                one_line_container,
                text="⚡ 0 MB/s | ⏱️ --:-- | 📦 0 MB",
                font=("Helvetica", 12),
                text_color="#666666",
                anchor="center",
                width=200
            )
            mini_stats.pack(side="left", padx=2)

            # 3. Mini pasek (po prawej) - z odstępem
            mini_progress = CTkProgressBar(
                one_line_container,
                width=80,
                height=6,
                fg_color="#2a2a2a",
                progress_color="#ff8c00",
                corner_radius=2
            )
            mini_progress.pack(side="right", padx=(15, 0))
            mini_progress.set(0)

            # Zapisz referencje
            mini_progress_bars[idx] = mini_progress
            mini_stats_labels[idx] = mini_stats

        # Frame z postępem globalnym
        global_progress_frame = CTkFrame(main_frame, fg_color=THEME_COLORS["secondary"], corner_radius=8)
        global_progress_frame.pack(fill="x", pady=(0, 10))

        # Status ogólny
        global_status_label = CTkLabel(
            global_progress_frame,
            text="⏳ Przygotowanie...",
            font=("Helvetica", 13, "bold"),
            text_color=THEME_COLORS["warning"]
        )
        global_status_label.pack(pady=(10, 5))

        # Pasek postępu globalny
        global_progress_bar = CTkProgressBar(
            global_progress_frame,
            height=16,
            fg_color=THEME_COLORS["bg_input"],
            progress_color=THEME_COLORS["accent"]
        )
        global_progress_bar.pack(fill="x", padx=15, pady=5)
        global_progress_bar.set(0)

        # Info o postępie (X/Y)
        progress_count_label = CTkLabel(
            global_progress_frame,
            text=f"0 / {len(selected_videos)} ukończone",
            font=("Helvetica", 12),
            text_color=THEME_COLORS["text_secondary"]
        )
        progress_count_label.pack(pady=(2, 10))

        # Przyciski kontroli
        control_frame = CTkFrame(main_frame, fg_color="transparent")
        control_frame.pack(fill="x")

        # Przycisk Anuluj
        def cancel_download():
            self.is_converting = False
            progress_window.destroy()
            logger.info("❌ Pobieranie playlisty anulowane")

        cancel_btn = CTkButton(
            control_frame,
            text="❌ Anuluj pobieranie",
            command=cancel_download,
            height=35,
            font=("Helvetica", 12, "bold"),
            fg_color="#501616",
            hover_color="#602020"
        )
        cancel_btn.pack(pady=5)

        # Rozpocznij pobieranie w osobnym wątku
        def download_thread():
            logger.info("🚀 Wątek download_thread rozpoczęty!")
            try:
                self.is_converting = True
                converter = YouTubeToMP3Converter(self.output_folder)
                bitrate = self.get_selected_bitrate()
                format_type = self.selected_format

                total_videos = len(selected_videos)
                success_count = 0

                logger.info(f"📋 ROZPOCZYNAM POBIERANIE {total_videos} WIDEO")

                for idx, video_data in enumerate(selected_videos, 1):
                    current_idx = idx

                    if not self.is_converting:
                        logger.warning("⚠️ Pobieranie anulowane przez użytkownika")
                        break

                    video_url = video_data.get('url', '')
                    video_title = video_data.get('title', f'Video {idx}')

                    logger.info(f"📹 [{idx}/{total_videos}] Tytuł: {video_title}")

                    if not video_url:
                        logger.error(f"❌ [{idx}/{total_videos}] Brak URL dla: {video_title}")
                        continue

                    # Aktualizuj status globalny
                    progress_window.after(0, lambda i=idx, t=total_videos:
                        global_status_label.configure(text=f"📥 Pobieranie {i}/{t}...")
                    )

                    # Callback dla aktualizacji mini paska i statystyk
                    def update_mini_progress(data):
                        if 'percentage' in data:
                            percent = data['percentage'] / 100.0
                            # Aktualizuj mini pasek dla tego pliku
                            if current_idx in mini_progress_bars:
                                progress_window.after(0, lambda p=percent, idx=current_idx:
                                    mini_progress_bars[idx].set(p)
                                )

                        # Aktualizuj statystyki mini dla tego pliku
                        if current_idx in mini_stats_labels:
                            speed_mb = data.get('speed', 0) / (1024 * 1024)
                            eta_sec = data.get('eta', 0)
                            downloaded_mb = data.get('downloaded', 0) / (1024 * 1024)

                            eta_min = eta_sec // 60
                            eta_s = eta_sec % 60

                            progress_window.after(0, lambda s=speed_mb, e_m=eta_min, e_s=eta_s, d=downloaded_mb, idx=current_idx:
                                mini_stats_labels[idx].configure(
                                    text=f"⚡ {s:.2f} MB/s | ⏱️ {e_m:02d}:{e_s:02d} | 📦 {d:.1f} MB",
                                    text_color=THEME_COLORS["text_secondary"]
                                )
                            )

                    # Konwertuj
                    success = converter.convert(
                        video_url,
                        progress_callback=update_mini_progress,
                        bitrate=bitrate,
                        allow_playlist=False,
                        format_type=format_type
                    )

                    if success:
                        success_count += 1

                        # Mini pasek na 100% i zielony
                        if current_idx in mini_progress_bars:
                            progress_window.after(0, lambda idx=current_idx:
                                mini_progress_bars[idx].set(1.0)
                            )
                            progress_window.after(0, lambda idx=current_idx:
                                mini_progress_bars[idx].configure(progress_color="#4caf50")
                            )

                        # Finalne statystyki dla mini paska
                        if current_idx in mini_stats_labels:
                            try:
                                files = list(Path(self.output_folder).glob(f"*{video_title[:20]}*"))
                                file_size_mb = files[0].stat().st_size / (1024 * 1024) if files else 0
                            except:
                                file_size_mb = 0

                            progress_window.after(0, lambda sz=file_size_mb, idx=current_idx:
                                mini_stats_labels[idx].configure(
                                    text=f"✅ {sz:.1f} MB | 100%",
                                    text_color="#4caf50"
                                )
                            )

                        # Aktualizuj postęp globalny
                        global_percent = success_count / total_videos
                        progress_window.after(0, lambda p=global_percent: global_progress_bar.set(p))
                        progress_window.after(0, lambda s=success_count, t=total_videos:
                            progress_count_label.configure(text=f"{s} / {t} ukończone")
                        )

                        # Dodaj do historii
                        try:
                            files = list(Path(self.output_folder).glob(f"*{video_title[:20]}*"))
                            file_size = files[0].stat().st_size if files else 0
                            self.download_history.add_download(video_title, video_url, format_type.lower(), file_size)
                        except:
                            pass

                # Zakończono
                if self.is_converting:
                    progress_window.after(0, lambda s=success_count, t=total_videos:
                        global_status_label.configure(
                            text=f"✅ Ukończono! Pobrano {s}/{t} wideo",
                            text_color=THEME_COLORS["success"]
                        )
                    )
                    progress_window.after(0, lambda: global_progress_bar.set(1.0))
                    progress_window.after(0, lambda: cancel_btn.configure(text="✅ Zamknij", fg_color=THEME_COLORS["accent"]))

                    # Dźwięk
                    if self.sound_enabled:
                        self.sound_manager.play_sound('complete')

                    logger.info(f"✅ Pobieranie playlisty zakończone: {success_count}/{total_videos}")

            except Exception as e:
                logger.error(f"❌ Błąd pobierania playlisty: {str(e)}")
                progress_window.after(0, lambda:
                    global_status_label.configure(text=f"❌ Błąd: {str(e)}", text_color="#ff6b6b")
                )
            finally:
                self.is_converting = False

        # Uruchom wątek pobierania
        thread = threading.Thread(target=download_thread, daemon=True)
        thread.start()

    def start_conversion(self):
        """
        # KOMENTARZ PL: Rozpoczyna konwersję
        # HASH_CONVERSION_START: Główna logika konwersji
        """
        url = self.url_entry.get().strip()

        if not url:
            messagebox.showerror("❌ Błąd", "Wklej link YouTube!")
            return

        logger.info(f"🚀 start_conversion - URL: {url[:50]}...")
        logger.info(f"📋 playlist_var.get() = {self.playlist_var.get()}")
        logger.info(f"📋 is_playlist = {self.is_playlist}")

        # Sprawdź czy zaznaczono playlistę
        if self.playlist_var.get():
            # Jeśli checkbox "Playlista" jest zaznaczony, ZAWSZE pokazujemy selektor
            logger.info("🎬 CHECKBOX PLAYLISTY ZAZNACZONY - URUCHAMIAM SELEKTOR")
            # Pokaż okno wyboru wideo z playlisty (które otworzy okno postępu)
            self.show_playlist_selector(url)
            # Selektor już obsługuje pobieranie przez nowe okno, więc kończymy tutaj
            return
        else:
            logger.info("❌ Checkbox playlisty nie zaznaczony - normalna konwersja")
            self.selected_playlist_videos = None

        # Wyłącz przyciski
        self.btn_convert.configure(state="disabled")
        self.btn_cancel.configure(state="normal")
        self.is_converting = True

        # Reset zmiennych postępu
        self.progress_start_time = 0
        self.progress_last_update = 0
        self.progress_downloaded = 0

        # Pokaż status
        self.progress_status_label.configure(
            text="Pobieranie...",
            text_color=THEME_COLORS["warning"]
        )
        self.progress_percent_label.configure(text="0%")
        self.progress_size_label.configure(text="0 MB")
        self.progress_speed_label.configure(text="0 MB/s")
        self.progress_eta_label.configure(text="--:--")
        self.progress_bar.set(0)

        # Konwertuj w oddzielnym wątku
        # HASH_THREADING_CONVERSION: Asynchroniczna konwersja
        thread = threading.Thread(target=self._conversion_thread, args=(url,))
        thread.daemon = True
        thread.start()

    def _conversion_thread(self, url):
        """
        # KOMENTARZ PL: Wątek do konwersji
        """
        try:
            self.converter = YouTubeToMP3Converter(self.output_folder)

            # Pobierz wybraną jakość i format
            bitrate = self.get_selected_bitrate()
            format_type = self.selected_format

            # Sprawdź czy mamy wybrane wideo z playlisty
            if self.selected_playlist_videos:
                # Pobieraj tylko wybrane wideo
                total_videos = len(self.selected_playlist_videos)
                logger.info(f"📋 Konwersja {total_videos} wybranych wideo | Format: {format_type} | Bitrate: {bitrate} kbps")

                success_count = 0

                for idx, video_data in enumerate(self.selected_playlist_videos, 1):
                    if not self.is_converting:
                        break

                    video_url = video_data['url']
                    video_title = video_data['title']

                    logger.info(f"📹 Pobieranie {idx}/{total_videos}: {video_title}")
                    self.progress_status_label.configure(text=f"Pobieranie {idx}/{total_videos}...")

                    success = self.converter.convert(
                        video_url,
                        progress_callback=self.update_progress,
                        bitrate=bitrate,
                        allow_playlist=False,  # Pojedyncze wideo
                        format_type=format_type
                    )

                    if success:
                        success_count += 1
                        # Dodaj do historii
                        try:
                            files = list(Path(self.output_folder).glob(f"*{video_title[:20]}*"))
                            file_size = files[0].stat().st_size if files else 0
                            self.download_history.add_download(video_title, video_url, format_type.lower(), file_size)
                        except:
                            pass

                # Pokaż wynik
                if success_count > 0 and self.is_converting:
                    self.progress_status_label.configure(
                        text=f"✅ Pobrano {success_count}/{total_videos}",
                        text_color=THEME_COLORS["success"]
                    )
                    self.progress_bar.set(1.0)
                    self.progress_eta_label.configure(text="00:00")

                    # Dźwięk powiadomienia
                    if self.sound_enabled:
                        self.sound_manager.play_sound('complete')

                    messagebox.showinfo("✅ Sukces", f"Pobrano {success_count}/{total_videos} wideo z playlisty!")
                    logger.info(f"✅ Konwersja zakończona: {success_count}/{total_videos} wideo")
                elif self.is_converting:
                    self.progress_status_label.configure(text="❌ Błąd", text_color="#ff6b6b")
                    if self.sound_enabled:
                        self.sound_manager.play_sound('error')
                    messagebox.showerror("❌ Błąd", "Nie udało się pobrać żadnego wideo!")

                return

            # Normalna konwersja (pojedyncze wideo lub cała playlista)
            allow_playlist = self.playlist_var.get()

            if allow_playlist:
                logger.info(f"📋 Konwersja playlisty | Format: {format_type} | Bitrate: {bitrate} kbps")
            else:
                logger.info(f"🎵 Konwersja | Format: {format_type} | Bitrate: {bitrate} kbps")


            success = self.converter.convert(
                url,
                progress_callback=self.update_progress,
                bitrate=bitrate,
                allow_playlist=allow_playlist,
                format_type=format_type
            )

            if success and self.is_converting:
                # Dodaj do historii
                title = "Unknown"
                try:
                    # Próbuj pobrać tytuł z video info
                    info = self.converter.get_video_info(url)
                    if info.get('valid'):
                        title = info.get('title', 'Unknown')
                except:
                    pass

                # Dodaj metadane ID3 (jeśli MP3)
                if format_type.lower() == 'mp3':
                    try:
                        # Znajdź pobrany plik
                        files = list(Path(self.output_folder).glob(f"{title}.*"))
                        if files:
                            file_path = str(files[0])
                            info = self.converter.get_video_info(url)
                            if info.get('valid'):
                                artist = info.get('channel', 'Unknown')
                                thumbnail = info.get('thumbnail', '')
                                self.converter.add_id3_tags(file_path, title, artist, thumbnail)
                    except Exception as e:
                        logger.warning(f"⚠️ Nie można dodać ID3 tagów: {str(e)}")

                # Dodaj do historii
                try:
                    file_size = 0
                    files = list(Path(self.output_folder).glob(f"{title}.*"))
                    if files:
                        file_size = files[0].stat().st_size
                    self.download_history.add_download(title, url, format_type.lower(), file_size)
                except Exception as e:
                    logger.warning(f"⚠️ Nie można dodać do historii: {str(e)}")

                self.progress_status_label.configure(
                    text="✅ Ukończone!",
                    text_color=THEME_COLORS["success"]
                )
                self.progress_bar.set(1.0)
                self.progress_eta_label.configure(text="00:00")
                logger.info("✅ Konwersja zakończona pomyślnie")

                # Dźwięk powiadomienia
                if self.sound_enabled:
                    self.sound_manager.play_sound('complete')

                messagebox.showinfo("✅ Sukces", f"Plik {format_type.upper()} został zapisany!")
            elif self.is_converting:
                self.progress_status_label.configure(
                    text="❌ Błąd",
                    text_color="#ff6b6b"
                )
                logger.error("❌ Konwersja nie powiodła się")

                # Dźwięk błędu
                if self.sound_enabled:
                    self.sound_manager.play_sound('error')

                messagebox.showerror("❌ Błąd", "Konwersja nie powiodła się")

        except Exception as e:
            if self.is_converting:
                self.progress_status_label.configure(
                    text=f"❌ Błąd: {str(e)}",
                    text_color="#ff6b6b"
                )
                logger.error(f"❌ Wyjątek: {str(e)}")

                # Dźwięk błędu
                if self.sound_enabled:
                    self.sound_manager.play_sound('error')

                messagebox.showerror("❌ Błąd", f"Błąd: {str(e)}")

        finally:
            # Przywróć przyciski
            self.btn_convert.configure(state="normal")
            self.btn_cancel.configure(state="disabled")
            self.is_converting = False

    def update_progress(self, data):
        """
        # KOMENTARZ PL: Aktualizuje pasek postępu z danymi dla nerda
        # HASH_PROGRESS_UPDATE: Callback dla postępu
        Przyjmuje: float (0.0-1.0) lub dict z kluczami: percentage, speed, eta, downloaded
        """
        import time

        # Kompatybilność wsteczna - jeśli data to float
        if isinstance(data, (int, float)):
            value = float(data)
            # Konwertuj na słownik
            data = {'percentage': value * 100}
        elif isinstance(data, dict):
            # Pobierz procent ze słownika
            value = data.get('percentage', 0) / 100.0
        else:
            return

        current_time = time.time()

        # Inicjalizuj czas startu
        if self.progress_start_time == 0:
            self.progress_start_time = current_time
            self.progress_last_update = current_time

        # Aktualizuj pasek
        self.progress_bar.set(value)
        percent = int(value * 100)

        # Procent
        self.progress_percent_label.configure(text=f"{percent}%")

        # Rozmiar - użyj danych ze słownika jeśli dostępne
        if isinstance(data, dict) and 'downloaded' in data:
            size_mb = data['downloaded'] / (1024 * 1024)
            self.progress_size_label.configure(text=f"{size_mb:.1f} MB")
        else:
            # Fallback - szacunkowy rozmiar
            elapsed = current_time - self.progress_start_time
            estimated_size_mb = (elapsed / 60.0) * 5
            self.progress_size_label.configure(text=f"{estimated_size_mb:.1f} MB")

        # Szybkość - użyj danych ze słownika jeśli dostępne
        if isinstance(data, dict) and 'speed' in data and data['speed'] > 0:
            speed_mb_s = data['speed'] / (1024 * 1024)
            self.progress_speed_label.configure(text=f"{speed_mb_s:.2f} MB/s")
        else:
            # Fallback - szacunkowa szybkość
            elapsed = current_time - self.progress_start_time
            if elapsed > 1:
                if isinstance(data, dict) and 'downloaded' in data:
                    speed_mb_s = (data['downloaded'] / (1024 * 1024)) / elapsed
                else:
                    estimated_size_mb = (elapsed / 60.0) * 5
                    speed_mb_s = estimated_size_mb / elapsed
                self.progress_speed_label.configure(text=f"{speed_mb_s:.2f} MB/s")

        # ETA - użyj danych ze słownika jeśli dostępne
        if isinstance(data, dict) and 'eta' in data and data['eta'] > 0:
            eta_minutes = int(data['eta'] // 60)
            eta_secs = int(data['eta'] % 60)
            self.progress_eta_label.configure(text=f"{eta_minutes:02d}:{eta_secs:02d}")
        elif value > 0 and value < 1:
            # Fallback - szacunkowy ETA
            elapsed = current_time - self.progress_start_time
            remaining_percent = 1.0 - value
            elapsed_per_percent = elapsed / value if value > 0 else 0
            eta_seconds = remaining_percent * elapsed_per_percent
            eta_minutes = int(eta_seconds // 60)
            eta_secs = int(eta_seconds % 60)
            self.progress_eta_label.configure(text=f"{eta_minutes:02d}:{eta_secs:02d}")
        elif value >= 1:
            self.progress_eta_label.configure(text="00:00")
            self.progress_status_label.configure(text="Kończę...")
        else:
            self.progress_eta_label.configure(text="--:--")

        self.progress_last_update = current_time

    def cancel_conversion(self):
        """
        # KOMENTARZ PL: Anuluje konwersję
        """
        self.is_converting = False
        self.btn_convert.configure(state="normal")
        self.btn_cancel.configure(state="disabled")
        self.progress_status_label.configure(
            text="❌ Anulowano",
            text_color="#ff6b6b"
        )
        logger.info("❌ Konwersja anulowana przez użytkownika")

    def check_ffmpeg_status(self):
        """
        # KOMENTARZ PL: Sprawdza status FFmpeg i aktualizuje UI
        """
        if self.ffmpeg_manager.is_ffmpeg_available():
            self.info_display.configure(
                text="✅ FFmpeg dostępny - gotowy do konwersji!\nWklej link YouTube i kliknij 'Sprawdź informacje'",
                text_color=THEME_COLORS["success"]
            )
            self.btn_install_ffmpeg.configure(text="✅ FFmpeg OK", state="disabled")
        else:
            self.info_display.configure(
                text="⚠️  FFmpeg nie jest zainstalowany\nKliknij 'Zainstaluj FFmpeg' lub zostanie pobrany automatycznie",
                text_color=THEME_COLORS["warning"]
            )
            self.btn_install_ffmpeg.configure(text="🔧 Zainstaluj FFmpeg", state="normal")

    def install_ffmpeg(self):
        """
        # KOMENTARZ PL: Instaluje FFmpeg ręcznie
        """
        self.btn_install_ffmpeg.configure(text="⏳ Instalowanie...", state="disabled")
        self.progress_status_label.configure(text="📥 Pobieranie FFmpeg...")
        self.progress_bar.set(0.1)

        # Instaluj w osobnym wątku
        thread = threading.Thread(target=self._install_ffmpeg_thread)
        thread.daemon = True
        thread.start()

    def _install_ffmpeg_thread(self):
        """Wątek instalacji FFmpeg"""
        try:
            success = self.ffmpeg_manager.download_ffmpeg()

            if success:
                self.progress_status_label.configure(
                    text="✅ FFmpeg OK",
                    text_color=THEME_COLORS["success"]
                )
                self.btn_install_ffmpeg.configure(text="✅ FFmpeg OK", state="disabled")
                messagebox.showinfo("✅ Sukces", "FFmpeg został zainstalowany!")
            else:
                self.progress_status_label.configure(
                    text="❌ Błąd FFmpeg",
                    text_color="#ff6b6b"
                )
                self.btn_install_ffmpeg.configure(text="🔧 Spróbuj ponownie", state="normal")
                messagebox.showerror("❌ Błąd", "Nie udało się zainstalować FFmpeg")

        except Exception as e:
            self.progress_status_label.configure(
                text=f"❌ Błąd: {str(e)[:20]}",
                text_color="#ff6b6b"
            )
            self.btn_install_ffmpeg.configure(text="🔧 Spróbuj ponownie", state="normal")
            logger.error(f"❌ Błąd instalacji: {str(e)}")

        finally:
            self.progress_bar.set(0)

# ═══════════════════════════════════════════════════════════════════════════
# GŁÓWNA FUNKCJA
# ═══════════════════════════════════════════════════════════════════════════

def main():
    """
    # KOMENTARZ PL: Punkt wejściowy aplikacji
    # HASH_MAIN_FUNCTION: Inicjalizacja i mainloop
    """
    logger.info("═" * 80)
    logger.info("🎵 YOUTUBE TO MP3 CONVERTER STARTED")
    logger.info(f"Autor: Stanisław Kozioł")
    logger.info(f"Czas uruchomienia: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("═" * 80)

    app = YouTubeMP3App()
    app.mainloop()

    logger.info("═" * 80)
    logger.info("🎵 YOUTUBE TO MP3 CONVERTER CLOSED")
    logger.info("═" * 80)

# ═══════════════════════════════════════════════════════════════════════════
# PUNKT WEJŚCIA
# ═══════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    main()

