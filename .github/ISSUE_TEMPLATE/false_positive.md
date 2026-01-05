---
name: 🛡️ False Positive Antivirus Detection
about: Report a false positive virus detection
title: '[FALSE POSITIVE] Antivirus flagged the application'
labels: 'false-positive, help-wanted'
assignees: ''
---

## Antivirus Information

**Which antivirus flagged the application?**
(e.g., Windows Defender, Avast, Norton, etc.)

**Detection name:**
(e.g., "Trojan:Win32/Wacatac", "PUA.Bundler", etc.)

**Version of the application:**
- [ ] Downloaded EXE from Releases
- [ ] Built from source
- [ ] Version: (e.g., 2.0.0)

## Steps to Reproduce

1. Downloaded file from: [provide link or release version]
2. Antivirus scan result: [paste detection message]
3. Operating System: [Windows 10/11, version]

## Additional Context

**Have you verified the file?**
- [ ] Yes, I checked the source code on GitHub
- [ ] Yes, I compared SHA256 hash
- [ ] No, I just downloaded and ran it

**Screenshots:**
If applicable, add screenshots of the antivirus detection.

---

## ℹ️ Information for Users

This is almost certainly a **false positive**. This application is:
- ✅ 100% open source (you can read all the code)
- ✅ Built with PyInstaller (legitimate Python packaging tool)
- ✅ Uses only trusted libraries (yt-dlp, customtkinter, etc.)
- ✅ No telemetry, no data collection
- ✅ MIT Licensed

**Common reasons for false positives:**
1. PyInstaller bundles Python runtime (looks suspicious to antivirus)
2. Application downloads files from internet (yt-dlp library)
3. FFmpeg media processing (file manipulation)
4. No code signing certificate (costs $300+/year for open source project)

**What you can do:**
1. **Add exception in your antivirus** - This is safe! Check the source code yourself.
2. **Run from source** instead of EXE:
   ```bash
   git clone https://github.com/crahdlinuxservers-maker/YouTubeToMP3.git
   cd YouTubeToMP3
   pip install -r requirements.txt
   python youtube_to_mp3.py
   ```
3. **Report false positive** to your antivirus vendor:
   - See: [REPORT_FALSE_POSITIVE.md](../REPORT_FALSE_POSITIVE.md)
   - See: [ANTIVIRUS_FALSE_POSITIVE.md](../ANTIVIRUS_FALSE_POSITIVE.md)

**For maintainers:**
- Add the detection details to known false positives list
- Update antivirus vendor submissions if needed
- Verify build process and PyInstaller flags

