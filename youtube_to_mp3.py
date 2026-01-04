"""
╔════════════════════════════════════════════════════════════════════════════╗
║                       YOUTUBE TO MP3 CONVERTER                             ║
║                        Konwerter YouTube → MP3                             ║
║                                                                             ║
║  Autor: Stanisław Kozioł                                                   ║
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
                progress_callback(0.2)

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
        if d['status'] == 'downloading':
            percent = d.get('_percent_str', '0%').strip('%')
            if self._progress_callback:
                try:
                    self._progress_callback(float(percent.replace('%', '')) / 100)
                except:
                    pass
        elif d['status'] == 'finished':
            if self._progress_callback:
                self._progress_callback(1.0)

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
        self.geometry("700x740")
        self.minsize(700, 740)
        self.maxsize(700, 740)
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

        title_label = CTkLabel(
            header_frame,
            text="🎵 YouTube to MP3 Converter",
            font=("Helvetica", 16, "bold"),
            text_color=THEME_COLORS["text_primary"]
        )
        title_label.pack(pady=4)

        subtitle_label = CTkLabel(
            header_frame,
            text="Pobierz muzykę z YouTube",
            font=("Helvetica", 8),
            text_color=THEME_COLORS["text_secondary"]
        )
        subtitle_label.pack(pady=(0, 2))

        # ═══════════════════════════════════════════════════════════════════
        # SEKCJA LINKU
        # ═══════════════════════════════════════════════════════════════════

        url_frame = CTkFrame(main_frame, fg_color=THEME_COLORS["secondary"], corner_radius=8)
        url_frame.pack(fill="x", pady=2)

        url_label = CTkLabel(
            url_frame,
            text="🔗 Link YouTube:",
            font=("Helvetica", 10, "bold"),
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
            font=("Helvetica", 10),
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

        # HASH_CHECK_INFO_BTN: Przycisk do pobierania informacji (przy URL)
        self.btn_check_info = CTkButton(
            url_input_frame,
            text="ℹ️ Sprawdź",
            command=self.check_video_info,
            height=32,
            font=("Helvetica", 10, "bold"),
            fg_color=THEME_COLORS["warning"],
            hover_color="#ffb84d",
            text_color=THEME_COLORS["primary"],
            corner_radius=6,
            width=90
        )
        self.btn_check_info.pack(side="right")

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
            font=("Helvetica", 9),
            text_color=THEME_COLORS["text_secondary"],
            justify="left",
            wraplength=380
        )
        self.info_display.pack(anchor="w", fill="both", expand=True, pady=2)

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
            font=("Helvetica", 8, "bold"),
            text_color=THEME_COLORS["text_primary"]
        )
        self.progress_percent_label.pack(side="left", padx=(0, 8))

        # Status
        self.progress_status_label = CTkLabel(
            progress_data_frame,
            text="Gotowy",
            font=("Helvetica", 8),
            text_color=THEME_COLORS["text_secondary"]
        )
        self.progress_status_label.pack(side="left", padx=(0, 12))

        # Rozmiar pobierany
        self.progress_size_label = CTkLabel(
            progress_data_frame,
            text="0 MB",
            font=("Helvetica", 8),
            text_color=THEME_COLORS["text_secondary"]
        )
        self.progress_size_label.pack(side="left", padx=(0, 12))

        # Szybkość
        self.progress_speed_label = CTkLabel(
            progress_data_frame,
            text="0 MB/s",
            font=("Helvetica", 8),
            text_color=THEME_COLORS["text_secondary"]
        )
        self.progress_speed_label.pack(side="left", padx=(0, 12))

        # ETA
        self.progress_eta_label = CTkLabel(
            progress_data_frame,
            text="--:--",
            font=("Helvetica", 8),
            text_color=THEME_COLORS["text_secondary"]
        )
        self.progress_eta_label.pack(side="left")

        folder_frame = CTkFrame(main_frame, fg_color=THEME_COLORS["secondary"], corner_radius=8)
        folder_frame.pack(fill="x", pady=2)

        folder_label = CTkLabel(
            folder_frame,
            text="📁 Folder:",
            font=("Helvetica", 10, "bold"),
            text_color=THEME_COLORS["text_primary"]
        )
        folder_label.pack(anchor="w", padx=12, pady=(4, 1))

        # HASH_FOLDER_DISPLAY: Wyświetlanie ścieżki folderu
        self.folder_display = CTkLabel(
            folder_frame,
            text=self.output_folder,
            font=("Helvetica", 7),
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
            font=("Helvetica", 9, "bold"),
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
            font=("Helvetica", 9, "bold"),
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
            font=("Helvetica", 10, "bold"),
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
            font=("Helvetica", 9),
            dropdown_font=("Helvetica", 8),
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

        # HASH_PLAYLIST_CHECKBOX: Checkbox dla playlist
        self.playlist_var = ctk.BooleanVar(value=False)
        self.playlist_checkbox = ctk.CTkCheckBox(
            quality_frame,
            text="📋 Playlista",
            variable=self.playlist_var,
            font=("Helvetica", 8),
            fg_color=THEME_COLORS["accent"],
            hover_color=THEME_COLORS["hover"],
            text_color=THEME_COLORS["text_secondary"],
            border_color=THEME_COLORS["accent"],
            checkbox_width=14,
            checkbox_height=14
        )
        self.playlist_checkbox.pack(anchor="w", padx=8, pady=(0, 4))

        # ═══════════════════════════════════════════════════════════════════
        # PRAWA STRONA: FORMAT AUDIO
        # ═══════════════════════════════════════════════════════════════════

        format_frame = CTkFrame(audio_settings_frame, fg_color=THEME_COLORS["secondary"], corner_radius=8)
        format_frame.pack(side="left", fill="both", expand=True, padx=(2, 0))

        format_label = CTkLabel(
            format_frame,
            text="🎵 Format:",
            font=("Helvetica", 10, "bold"),
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
            font=("Helvetica", 9),
            dropdown_font=("Helvetica", 8),
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

        # Przycisk statystyk
        self.btn_stats = CTkButton(
            format_selector_frame,
            text="📊",
            command=self.show_statistics,
            height=24,
            font=("Helvetica", 10, "bold"),
            fg_color=THEME_COLORS["warning"],
            hover_color="#ffb84d",
            text_color=THEME_COLORS["primary"],
            corner_radius=6,
            width=35
        )
        self.btn_stats.pack(side="left", padx=(4, 0))


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
            font=("Helvetica", 10, "bold"),
            fg_color=THEME_COLORS["accent"],
            hover_color=THEME_COLORS["hover"],
            text_color=THEME_COLORS["text_primary"],
            corner_radius=6
        )
        self.btn_convert.pack(side="left", padx=2, fill="both", expand=True)

        # Przycisk anulowania
        # HASH_CANCEL_BTN: Przycisk anulowania
        self.btn_cancel = CTkButton(
            button_frame,
            text="❌ Anuluj",
            command=self.cancel_conversion,
            height=26,
            font=("Helvetica", 10, "bold"),
            fg_color="#444444",
            hover_color="#555555",
            text_color=THEME_COLORS["text_primary"],
            corner_radius=6,
            state="disabled"
        )
        self.btn_cancel.pack(side="left", padx=2, fill="both", expand=True)

        # Przycisk wyczyść wyszukiwanie
        # HASH_CLEAR_SEARCH_BTN: Przycisk resetowania wyszukiwania
        self.btn_clear_search = CTkButton(
            button_frame,
            text="🔄 Wyczyść",
            command=self.clear_search,
            height=26,
            font=("Helvetica", 10, "bold"),
            fg_color="#555555",
            hover_color="#666666",
            text_color=THEME_COLORS["text_primary"],
            corner_radius=6
        )
        self.btn_clear_search.pack(side="left", padx=2, fill="both", expand=True)

        # Przycisk dźwięku
        # HASH_SOUND_BTN: Przycisk włączania dźwięku
        self.sound_enabled = self.app_config.get('sound_enabled', True)
        sound_text = "🔊 Dźwięk" if self.sound_enabled else "🔇 Cicho"
        self.btn_sound = CTkButton(
            button_frame,
            text=sound_text,
            command=self.toggle_sound,
            height=26,
            font=("Helvetica", 10, "bold"),
            fg_color="#555555",
            hover_color="#666666",
            text_color=THEME_COLORS["text_primary"],
            corner_radius=6
        )
        self.btn_sound.pack(side="left", padx=2, fill="both", expand=True)

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
        # KOMENTARZ PL: Wyświetla statystyki pobrań
        # HASH_STATISTICS: Historia i analityka
        """
        stats = self.download_history.get_statistics()
        history = self.download_history.get_history(limit=5)

        # Stwórz okno statystyk
        stats_window = ctk.CTkToplevel(self)
        stats_window.title("📊 Statystyki Pobrań")
        stats_window.geometry("400x300")
        stats_window.resizable(False, False)

        # Tytuł
        title_label = CTkLabel(
            stats_window,
            text="📊 Statystyki Pobrań",
            font=("Helvetica", 14, "bold"),
            text_color=THEME_COLORS["text_primary"]
        )
        title_label.pack(pady=10)

        # Główna rama
        content_frame = CTkFrame(stats_window, fg_color=THEME_COLORS["secondary"], corner_radius=8)
        content_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Statystyki
        stats_text = f"""
📥 Łączne pobrani: {stats['total_downloads']}
💾 Całkowity rozmiar: {stats['total_size_mb']} MB
🎵 Ulubiony format: {stats['favorite_format'].upper()}
        """

        stats_label = CTkLabel(
            content_frame,
            text=stats_text.strip(),
            font=("Helvetica", 11),
            text_color=THEME_COLORS["text_primary"],
            justify="left"
        )
        stats_label.pack(anchor="w", padx=15, pady=15)

        # Historia
        if history:
            history_text = "\n🕐 Ostatnie pobrania:\n"
            for idx, (title, date, format_t, size) in enumerate(history[:3], 1):
                history_text += f"{idx}. {title[:25]}... ({format_t})\n"

            history_label = CTkLabel(
                content_frame,
                text=history_text,
                font=("Helvetica", 9),
                text_color=THEME_COLORS["text_secondary"],
                justify="left",
                wraplength=350
            )
            history_label.pack(anchor="w", padx=15, pady=(0, 10))

        # Przycisk czyszczenia
        def clear_hist():
            self.download_history.clear_history()
            messagebox.showinfo("✅ Sukces", "Historia czyszczona!")
            stats_window.destroy()

        btn_clear = CTkButton(
            content_frame,
            text="🗑️ Wyczyść historię",
            command=clear_hist,
            height=26,
            font=("Helvetica", 9, "bold"),
            fg_color=THEME_COLORS["accent"],
            hover_color=THEME_COLORS["hover"],
            text_color=THEME_COLORS["text_primary"],
            corner_radius=6
        )
        btn_clear.pack(pady=10)

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
        # HASH_PLAYLIST_SELECTOR: Wybór wideo z playlisty
        """
        logger.info(f"🎬 show_playlist_selector uruchomiony dla: {url[:50]}...")

        # Pobierz informacje o playliście
        try:
            converter = YouTubeToMP3Converter(self.output_folder)

            # Pokaż status
            self.progress_status_label.configure(text="Pobieranie playlisty...", text_color=THEME_COLORS["warning"])
            self.update()
            logger.info("📊 Pobieranie listy wideo z playlisty...")

            # Użyj yt-dlp do pobrania listy wideo
            from yt_dlp import YoutubeDL

            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'extract_flat': 'in_playlist',
                'skip_download': True,
            }

            with YoutubeDL(ydl_opts) as ydl:
                playlist_info = ydl.extract_info(url, download=False)

            if playlist_info.get('_type') != 'playlist':
                # Fallback: sprawdź czy ma entries
                entries = playlist_info.get('entries', [])
                if not entries or len(entries) < 1:
                    messagebox.showwarning("⚠️ Ostrzeżenie", "To nie jest playlista lub playlista jest pusta!")
                    logger.warning(f"⚠️ Nie znaleziono playlisty - _type: {playlist_info.get('_type')}, entries: {len(entries)}")
                    return None
            else:
                entries = playlist_info.get('entries', [])

            if not entries:
                messagebox.showwarning("⚠️ Ostrzeżenie", "Playlista jest pusta!")
                return None

            # Stwórz okno wyboru
            selector_window = ctk.CTkToplevel(self)
            selector_window.title(f"📋 Wybierz wideo z playlisty ({len(entries)} wideo)")
            selector_window.geometry("700x650")
            selector_window.minsize(600, 400)
            selector_window.resizable(True, True)

            # Wycentruj okno
            selector_window.transient(self)
            selector_window.grab_set()

            # Nagłówek
            header = CTkLabel(
                selector_window,
                text=f"📋 {playlist_info.get('title', 'Playlista')}",
                font=("Helvetica", 14, "bold"),
                text_color=THEME_COLORS["text_primary"]
            )
            header.pack(pady=10, padx=10)

            subtitle = CTkLabel(
                selector_window,
                text=f"Wybierz wideo do pobrania ({len(entries)} dostępnych)",
                font=("Helvetica", 10),
                text_color=THEME_COLORS["text_secondary"]
            )
            subtitle.pack(pady=(0, 10))

            # Frame z przyciskami zaznacz wszystkie/odznacz wszystkie
            select_frame = CTkFrame(selector_window, fg_color="transparent")
            select_frame.pack(fill="x", padx=10, pady=5)

            def select_all():
                for var in checkbox_vars:
                    var.set(True)

            def deselect_all():
                for var in checkbox_vars:
                    var.set(False)

            btn_select_all = CTkButton(
                select_frame,
                text="✅ Zaznacz wszystkie",
                command=select_all,
                height=26,
                font=("Helvetica", 9, "bold"),
                fg_color=THEME_COLORS["accent"],
                hover_color=THEME_COLORS["hover"],
                width=140
            )
            btn_select_all.pack(side="left", padx=5)

            btn_deselect_all = CTkButton(
                select_frame,
                text="❌ Odznacz wszystkie",
                command=deselect_all,
                height=26,
                font=("Helvetica", 9, "bold"),
                fg_color="#555555",
                hover_color="#666666",
                width=140
            )
            btn_deselect_all.pack(side="left", padx=5)

            # ===== PAGINACJA =====
            ITEMS_PER_PAGE = 50  # Ile wideo na jedną stronę
            total_videos = len(entries)
            total_pages = (total_videos + ITEMS_PER_PAGE - 1) // ITEMS_PER_PAGE
            current_page = [0]  # Używamy listy aby można było zmienić wartość w nested function

            # Lista checkboxów (wszystkie)
            checkbox_vars = []
            selected_videos = []

            # Frame dla stron
            page_frame = CTkFrame(selector_window, fg_color="transparent")
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
                corner_radius=8
            )
            scroll_frame.pack(fill="both", expand=True, pady=(0, 10))

            def render_page(page_idx):
                """Renderuje wideo dla danej strony"""
                # Wyczyść poprzednie wideo
                for widget in scroll_frame.winfo_children():
                    widget.destroy()

                # Oblicz range
                start_idx = page_idx * ITEMS_PER_PAGE
                end_idx = min(start_idx + ITEMS_PER_PAGE, total_videos)

                logger.info(f"📄 Renderowanie strona {page_idx + 1}: wideo {start_idx + 1} do {end_idx}")

                # Renderuj wideo na tej stronie
                for i, entry in enumerate(entries[start_idx:end_idx], start_idx + 1):
                    if not entry:
                        continue

                    try:
                        title = entry.get('title', f'Video {i}')
                        if not title:
                            title = f'Video {i}'

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

                        # Checkbox variable
                        var = ctk.BooleanVar(value=True)
                        checkbox_vars.append(var)

                        # Checkbox z tytułem
                        if duration and duration > 0:
                            duration_str = f"{duration // 60}:{duration % 60:02d}"
                        else:
                            duration_str = "?"

                        checkbox_text = f"{i}. {title[:40]}{'...' if len(title) > 40 else ''} ({duration_str})"

                        checkbox = ctk.CTkCheckBox(
                            video_frame,
                            text=checkbox_text,
                            variable=var,
                            font=("Helvetica", 8),
                            fg_color=THEME_COLORS["accent"],
                            hover_color=THEME_COLORS["hover"],
                            text_color=THEME_COLORS["text_secondary"],
                            checkbox_width=14,
                            checkbox_height=14
                        )
                        checkbox.pack(anchor="w", padx=6, pady=4)

                        # Zapisz dane wideo
                        video_url = entry.get('url')
                        if not video_url:
                            video_id = entry.get('id', '')
                            if video_id:
                                video_url = f"https://www.youtube.com/watch?v={video_id}"
                            else:
                                video_url = ""

                        selected_videos.append({
                            'var': var,
                            'entry': entry,
                            'title': title,
                            'url': video_url
                        })

                    except Exception as e:
                        logger.error(f"⚠️ Błąd dodawania wideo {i}: {str(e)}")
                        continue

                # Aktualizuj info o stronie
                page_info_label.configure(
                    text=f"Strona {page_idx + 1} z {total_pages} (Wideo {start_idx + 1}-{end_idx} z {total_videos})"
                )

            # Renderuj pierwszą stronę
            render_page(0)

            # Frame z przyciskami nawigacji
            nav_frame = CTkFrame(selector_window, fg_color="transparent")
            nav_frame.pack(fill="x", padx=10, pady=5)

            def prev_page():
                if current_page[0] > 0:
                    current_page[0] -= 1
                    render_page(current_page[0])
                    logger.info(f"⬅️ Poprzednia strona: {current_page[0] + 1}")

            def next_page():
                if current_page[0] < total_pages - 1:
                    current_page[0] += 1
                    render_page(current_page[0])
                    logger.info(f"➡️ Następna strona: {current_page[0] + 1}")

            btn_prev = CTkButton(
                nav_frame,
                text="⬅️ Poprzednia",
                command=prev_page,
                height=26,
                font=("Helvetica", 9, "bold"),
                fg_color="#555555",
                hover_color="#666666",
                state="disabled" if total_pages <= 1 else "normal"
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
                command=next_page,
                height=26,
                font=("Helvetica", 9, "bold"),
                fg_color="#555555",
                hover_color="#666666",
                state="disabled" if total_pages <= 1 else "normal"
            )
            btn_next.pack(side="left", padx=5, expand=True, fill="x")                except Exception as e:
                    logger.error(f"⚠️ Błąd dodawania wideo {idx}: {str(e)}")
                    continue

            # Frame z przyciskami OK/Anuluj
            button_frame = CTkFrame(selector_window, fg_color="transparent")
            button_frame.pack(fill="x", padx=10, pady=10)

            result = {'confirmed': False, 'selected': []}

            def confirm():
                # Zbierz zaznaczone wideo
                result['selected'] = [v for v in selected_videos if v['var'].get()]
                result['confirmed'] = True
                selector_window.destroy()

            def cancel():
                result['confirmed'] = False
                selector_window.destroy()

            btn_ok = CTkButton(
                button_frame,
                text=f"▶️ Pobierz zaznaczone",
                command=confirm,
                height=32,
                font=("Helvetica", 11, "bold"),
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
                font=("Helvetica", 11, "bold"),
                fg_color="#555555",
                hover_color="#666666",
                width=120
            )
            btn_cancel.pack(side="left", padx=5)

            # Czekaj aż okno się zamknie
            self.wait_window(selector_window)

            self.progress_status_label.configure(text="Gotowy", text_color=THEME_COLORS["text_secondary"])

            if result['confirmed'] and result['selected']:
                logger.info(f"✅ Wybrano {len(result['selected'])} wideo z playlisty")
                return result['selected']
            else:
                logger.info("❌ Anulowano wybór playlisty")
                return None

        except Exception as e:
            logger.error(f"❌ Błąd pobierania playlisty: {str(e)}")
            messagebox.showerror("❌ Błąd", f"Nie można pobrać playlisty:\n{str(e)}")
            return None

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
            # Pokaż okno wyboru wideo z playlisty
            selected_videos = self.show_playlist_selector(url)
            logger.info(f"📋 Selektor zwrócił: {selected_videos}")

            if not selected_videos:
                # Użytkownik anulował lub nic nie wybrał
                logger.info("❌ Użytkownik anulował selektor")
                return

            # Zapisz wybrane wideo do zmiennej
            self.selected_playlist_videos = selected_videos
            logger.info(f"📋 Rozpoczynam pobieranie {len(selected_videos)} wybranych wideo")
        else:
            logger.info("❌ Checkbox playlisty nie zaznaczony - normalna konwersja")
            self.selected_playlist_videos = None

        # Wyłącz przyciski
        self.btn_convert.configure(state="disabled")
        self.btn_check_info.configure(state="disabled")
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
            self.btn_check_info.configure(state="normal")
            self.btn_cancel.configure(state="disabled")
            self.is_converting = False

    def update_progress(self, value):
        """
        # KOMENTARZ PL: Aktualizuje pasek postępu z danymi dla nerda
        # HASH_PROGRESS_UPDATE: Callback dla postępu
        """
        import time

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

        # Szacunkowy rozmiar pobierany (zakładając ~5MB na minutę)
        elapsed = current_time - self.progress_start_time
        estimated_size_mb = (elapsed / 60.0) * 5  # ~5 MB/min to średnia
        self.progress_size_label.configure(text=f"{estimated_size_mb:.1f} MB")

        # Szybkość (MB/s)
        if elapsed > 1:
            speed_mb_s = estimated_size_mb / elapsed
            self.progress_speed_label.configure(text=f"{speed_mb_s:.2f} MB/s")

        # ETA (pozostały czas)
        if value > 0 and value < 1:
            remaining_percent = 1.0 - value
            elapsed_per_percent = elapsed / value
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
        self.btn_check_info.configure(state="normal")
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

