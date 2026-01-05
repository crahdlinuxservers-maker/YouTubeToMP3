# System Requirements for YouTube to MP3 Converter

## Minimum Requirements

### All Platforms
- **Python**: 3.8 or higher (recommended: 3.10+)
- **RAM**: 512 MB minimum, 1 GB recommended
- **Storage**: 100 MB for application + space for downloads
- **Internet**: Required for downloading from YouTube

### Platform-Specific

#### Windows
- **OS**: Windows 7 or higher (Windows 10/11 recommended)
- **FFmpeg**: Automatically downloaded by the application
- **Visual C++ Redistributable**: May be required for some dependencies

#### Linux
- **OS**: Any modern distribution (Ubuntu 20.04+, Fedora 35+, Arch, etc.)
- **FFmpeg**: Must be installed (see README.md for instructions)
- **Python Tkinter**: Usually included, but may need separate installation
  - Ubuntu/Debian: `sudo apt install python3-tk`
  - Fedora: `sudo dnf install python3-tkinter`
  - Arch: `sudo pacman -S tk`

#### macOS
- **OS**: macOS 10.13 (High Sierra) or higher
- **FFmpeg**: Install via Homebrew (see README.md)
- **Python**: System Python or Homebrew Python

## Dependencies

All Python dependencies are listed in `requirements.txt`:
- customtkinter >= 5.2.0
- yt-dlp >= 2023.10.13
- Pillow >= 10.0.0
- mutagen >= 1.47.0
- requests >= 2.31.0

## Tested Platforms

✅ **Windows 10/11** - Fully tested and supported
✅ **Ubuntu 22.04 LTS** - Fully tested and supported
✅ **Fedora 38+** - Tested and supported
✅ **Arch Linux** - Tested and supported
✅ **macOS 13 (Ventura)** - Tested and supported

## Notes

- **GPU Acceleration**: Not required, CPU-only processing
- **Display**: Minimum resolution 1024x768 (recommended: 1920x1080)
- **Fonts**: Standard system fonts are used (Helvetica, Courier New)
- **Network**: No proxy configuration required in most cases

