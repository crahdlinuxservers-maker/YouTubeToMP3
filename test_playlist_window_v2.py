"""
Test okna pobierania playlisty - KAŻDY PLIK MA SWÓJ STATUS!
MEGA NERDERSKIE - indywidualne paski postępu dla każdego pliku
"""
import customtkinter as ctk
from customtkinter import CTkFrame, CTkLabel, CTkProgressBar, CTkButton
import time
import threading

# Kolory z głównego programu
THEME_COLORS = {
    "primary": "#1a1a1a",
    "secondary": "#2b2b2b",
    "accent": "#ff8c00",
    "hover": "#ffa500",
    "success": "#4caf50",
    "warning": "#ff9800",
    "text_primary": "#ffffff",
    "text_secondary": "#b0b0b0",
    "bg_input": "#333333"
}

# Dane testowe - więcej plików dla realizmu
test_videos = [
    {'title': 'AC/DC - Back In Black (Official Video)', 'url': 'https://youtube.com/watch?v=test1'},
    {'title': 'Queen - Bohemian Rhapsody (Official Video)', 'url': 'https://youtube.com/watch?v=test2'},
    {'title': 'Led Zeppelin - Stairway To Heaven', 'url': 'https://youtube.com/watch?v=test3'},
    {'title': 'Pink Floyd - Comfortably Numb (Pulse 1994)', 'url': 'https://youtube.com/watch?v=test4'},
    {'title': 'Guns N\' Roses - Sweet Child O\' Mine', 'url': 'https://youtube.com/watch?v=test5'},
    {'title': 'Metallica - Enter Sandman (Official Music Video)', 'url': 'https://youtube.com/watch?v=test6'},
    {'title': 'Nirvana - Smells Like Teen Spirit', 'url': 'https://youtube.com/watch?v=test7'},
    {'title': 'The Eagles - Hotel California (Live 1977)', 'url': 'https://youtube.com/watch?v=test8'},
]

def show_playlist_download_progress(selected_videos):
    """
    Okno postępu - KAŻDY PLIK Z WŁASNYM STATUSEM
    """
    # Okno
    progress_window = ctk.CTk()
    progress_window.title(f"📥 Batch Download Manager ({len(selected_videos)} files)")
    progress_window.geometry("950x820")
    progress_window.resizable(False, False)

    # Główny frame
    main_frame = CTkFrame(progress_window, fg_color=THEME_COLORS["primary"])
    main_frame.pack(fill="both", expand=True, padx=15, pady=15)

    # ASCII Art Nagłówek
    ascii_header = f"""
╔═══════════════════════════════════════════════════════════════════╗
║     🎵  YOUTUBE BATCH DOWNLOADER v2.0  🎵                         ║
║     [ PARALLEL PROCESSING - {len(selected_videos)} FILES IN QUEUE ]                        ║
╚═══════════════════════════════════════════════════════════════════╝
    """

    header_ascii = CTkLabel(
        main_frame,
        text=ascii_header,
        font=("Courier New", 9, "bold"),
        text_color=THEME_COLORS["accent"],
        justify="left"
    )
    header_ascii.pack(pady=(0, 5))

    # SEKCJA LISTY - KAŻDY PLIK MA SWÓJ PASEK!
    list_container = CTkFrame(main_frame, fg_color=THEME_COLORS["secondary"], corner_radius=8)
    list_container.pack(fill="both", expand=True, pady=(0, 10))

    list_header = CTkLabel(
        list_container,
        text="📋 DOWNLOAD QUEUE - INDIVIDUAL FILE STATUS:",
        font=("Courier New", 11, "bold"),
        text_color="#00ff00"
    )
    list_header.pack(anchor="w", padx=10, pady=(8, 4))

    list_scroll = ctk.CTkScrollableFrame(
        list_container,
        fg_color="#0a0a0a",
        corner_radius=6,
        height=400
    )
    list_scroll.pack(fill="both", expand=True, padx=10, pady=(0, 10))

    # Słownik widgetów dla każdego pliku
    file_widgets = {}

    # Buduj listę - KAŻDY PLIK Z WŁASNYM STATUSEM
    for idx, video in enumerate(selected_videos, 1):
        # Container
        file_container = CTkFrame(list_scroll, fg_color=THEME_COLORS["bg_input"], corner_radius=4)
        file_container.pack(fill="x", pady=3, padx=4)

        # Nagłówek pliku (tytuł + status)
        title_frame = CTkFrame(file_container, fg_color="transparent")
        title_frame.pack(fill="x", padx=8, pady=(6, 2))

        title = video.get('title', f'Video {idx}')
        file_title = CTkLabel(
            title_frame,
            text=f"[{idx:03d}] {title[:48]}{'...' if len(title) > 48 else ''}",
            font=("Courier New", 9),
            text_color="#00ff00",
            anchor="w"
        )
        file_title.pack(side="left")

        file_status = CTkLabel(
            title_frame,
            text="[ QUEUED ]",
            font=("Courier New", 9, "bold"),
            text_color="#666666",
            anchor="e"
        )
        file_status.pack(side="right", padx=5)

        # Pasek postępu
        file_progress = CTkProgressBar(
            file_container,
            height=10,
            fg_color="#1a1a1a",
            progress_color="#00ff00"
        )
        file_progress.pack(fill="x", padx=8, pady=(2, 2))
        file_progress.set(0)

        # Statystyki pliku
        file_stats_frame = CTkFrame(file_container, fg_color="transparent")
        file_stats_frame.pack(fill="x", padx=8, pady=(2, 6))

        file_stats = CTkLabel(
            file_stats_frame,
            text="⏳ Waiting in queue... | 0% | 0 MB/s | 0 MB",
            font=("Courier New", 8),
            text_color="#666666",
            anchor="w"
        )
        file_stats.pack(side="left")

        # Zapisz referencje
        file_widgets[idx] = {
            'container': file_container,
            'title': file_title,
            'status': file_status,
            'progress': file_progress,
            'stats': file_stats
        }

    # STATYSTYKI GLOBALNE
    stats_global = CTkFrame(main_frame, fg_color=THEME_COLORS["secondary"], corner_radius=8)
    stats_global.pack(fill="x", pady=(0, 10))

    stats_header = CTkLabel(
        stats_global,
        text="📊 BATCH STATISTICS",
        font=("Courier New", 10, "bold"),
        text_color="#00ff00"
    )
    stats_header.pack(pady=(8, 5))

    stats_grid = CTkFrame(stats_global, fg_color="transparent")
    stats_grid.pack(fill="x", padx=15, pady=(0, 10))

    total_time_label = CTkLabel(stats_grid, text="⏱️ TIME: 00:00", font=("Courier New", 10), text_color=THEME_COLORS["text_secondary"])
    total_time_label.pack(side="left", padx=10)

    total_size_label = CTkLabel(stats_grid, text="📦 SIZE: 0 MB", font=("Courier New", 10), text_color=THEME_COLORS["text_secondary"])
    total_size_label.pack(side="left", padx=10)

    avg_speed_label = CTkLabel(stats_grid, text="⚡ AVG: 0 MB/s", font=("Courier New", 10), text_color=THEME_COLORS["text_secondary"])
    avg_speed_label.pack(side="left", padx=10)

    # STATUS GLOBALNY
    status_frame = CTkFrame(main_frame, fg_color=THEME_COLORS["secondary"], corner_radius=8)
    status_frame.pack(fill="x", pady=(0, 10))

    global_status = CTkLabel(
        status_frame,
        text=">>> SYSTEM READY - PRESS START",
        font=("Courier New", 11, "bold"),
        text_color="#ffff00"
    )
    global_status.pack(pady=(10, 5))

    progress_count = CTkLabel(
        status_frame,
        text=f"FILES: 0/{len(selected_videos)} | ✓ SUCCESS: 0 | ✗ FAILED: 0",
        font=("Courier New", 10, "bold"),
        text_color=THEME_COLORS["accent"]
    )
    progress_count.pack(pady=(0, 10))

    # TERMINAL LOG
    terminal_container = CTkFrame(main_frame, fg_color=THEME_COLORS["secondary"], corner_radius=8)
    terminal_container.pack(fill="x", pady=(0, 10))

    terminal_header = CTkLabel(
        terminal_container,
        text="📟 SYSTEM LOG:",
        font=("Courier New", 10, "bold"),
        text_color="#00ff00"
    )
    terminal_header.pack(anchor="w", padx=10, pady=(8, 4))

    terminal_scroll = ctk.CTkScrollableFrame(
        terminal_container,
        fg_color="#0a0a0a",
        corner_radius=6,
        height=80
    )
    terminal_scroll.pack(fill="x", padx=10, pady=(0, 10))

    terminal_output = CTkLabel(
        terminal_scroll,
        text=">>> System initialized...\n>>> Ready for batch processing...",
        font=("Courier New", 9),
        text_color="#00ff00",
        justify="left",
        anchor="nw"
    )
    terminal_output.pack(fill="both", expand=True)

    # Funkcja logowania
    terminal_logs = []
    def add_log(msg):
        terminal_logs.append(f">>> {msg}")
        if len(terminal_logs) > 6:
            terminal_logs.pop(0)
        terminal_output.configure(text="\n".join(terminal_logs))

    # PRZYCISKI
    control_frame = CTkFrame(main_frame, fg_color="transparent")
    control_frame.pack(fill="x")

    close_btn = CTkButton(
        control_frame,
        text="[ ESC ] CLOSE WINDOW",
        command=progress_window.destroy,
        height=35,
        font=("Courier New", 11, "bold"),
        fg_color="#501616",
        hover_color="#602020",
        text_color="#ff0000"
    )
    close_btn.pack(pady=5)

    # SYMULACJA POBIERANIA - KAŻDY PLIK OSOBNO!
    def demo_download():
        import random
        start_time = time.time()
        total_size = 0
        success_count = 0
        failed_count = 0

        add_log("Batch download initialized...")
        progress_window.after(0, lambda: global_status.configure(text=">>> BATCH DOWNLOAD IN PROGRESS..."))
        time.sleep(0.5)

        for i in range(1, len(selected_videos) + 1):
            video_title = selected_videos[i-1]['title']
            widgets = file_widgets[i]

            # Status: DOWNLOADING
            progress_window.after(0, lambda w=widgets: w['status'].configure(text="[ DOWNLOADING ]", text_color="#ffff00"))
            progress_window.after(0, lambda w=widgets: w['container'].configure(fg_color="#3d3d1a"))
            progress_window.after(0, lambda idx=i, title=video_title: add_log(f"[{idx:03d}] {title[:30]}..."))

            # Animacja pobierania
            file_size = random.uniform(8, 25)
            for percent in range(0, 101, 5):
                speed = random.uniform(3.0, 9.0)
                eta_sec = max(0, int((100-percent) * 0.5))

                progress_window.after(0, lambda w=widgets, p=percent: w['progress'].set(p/100))
                progress_window.after(0, lambda w=widgets, p=percent, s=speed, e=eta_sec, fs=file_size:
                    w['stats'].configure(
                        text=f"📥 {p}% | ⚡ {s:.2f} MB/s | ⏱️ {e}s | 📦 {(p*fs/100):.1f} MB",
                        text_color="#00ff00"
                    )
                )
                time.sleep(0.035)

            # Sukces lub failure (85% sukces)
            is_success = random.random() > 0.15

            if is_success:
                # SUKCES
                progress_window.after(0, lambda w=widgets: w['status'].configure(text="[ ✓ DONE ]", text_color="#00ff00"))
                progress_window.after(0, lambda w=widgets: w['container'].configure(fg_color="#1a3d1a"))
                progress_window.after(0, lambda w=widgets, fs=file_size: w['stats'].configure(
                    text=f"✅ Complete | 📦 {fs:.1f} MB | 100% | ⚡ Ready",
                    text_color="#00ff00"
                ))
                success_count += 1
                total_size += file_size
                progress_window.after(0, lambda idx=i: add_log(f"[{idx:03d}] ✓ Success!"))
            else:
                # FAILURE
                progress_window.after(0, lambda w=widgets: w['status'].configure(text="[ ✗ FAILED ]", text_color="#ff0000"))
                progress_window.after(0, lambda w=widgets: w['container'].configure(fg_color="#3d1a1a"))
                progress_window.after(0, lambda w=widgets: w['stats'].configure(
                    text=f"❌ Error: Connection timeout (network issue)",
                    text_color="#ff6666"
                ))
                progress_window.after(0, lambda w=widgets: w['progress'].configure(progress_color="#ff0000"))
                progress_window.after(0, lambda w=widgets: w['mini_progress'].configure(progress_color="rgba(255, 0, 0, 0.6)"))
                failed_count += 1
                progress_window.after(0, lambda idx=i: add_log(f"[{idx:03d}] ✗ Failed!"))

            elapsed = time.time() - start_time
            avg_speed = total_size / elapsed if elapsed > 0 else 0

            # Statystyki globalne
            progress_window.after(0, lambda e=elapsed: total_time_label.configure(text=f"⏱️ TIME: {int(e//60):02d}:{int(e%60):02d}"))
            progress_window.after(0, lambda ts=total_size: total_size_label.configure(text=f"📦 SIZE: {ts:.1f} MB"))
            progress_window.after(0, lambda avg=avg_speed: avg_speed_label.configure(text=f"⚡ AVG: {avg:.2f} MB/s"))

            # Licznik
            progress_window.after(0, lambda idx=i, s=success_count, f=failed_count:
                progress_count.configure(text=f"FILES: {idx}/{len(selected_videos)} | ✓ SUCCESS: {s} | ✗ FAILED: {f}")
            )

            time.sleep(0.1)

        # Zakończono
        if failed_count == 0:
            progress_window.after(0, lambda: global_status.configure(
                text=f">>> ALL DOWNLOADS COMPLETED! [{success_count}/{len(selected_videos)}] ✓",
                text_color="#00ff00"
            ))
            progress_window.after(0, lambda s=success_count: add_log(f"✓ Perfect! All {s} files OK!"))
        else:
            progress_window.after(0, lambda: global_status.configure(
                text=f">>> BATCH COMPLETED WITH ERRORS! [✓ {success_count} | ✗ {failed_count}]",
                text_color="#ff9800"
            ))
            progress_window.after(0, lambda s=success_count, f=failed_count: add_log(f"⚠ Done! Success: {s}, Failed: {f}"))

        progress_window.after(0, lambda ts=total_size: add_log(f"Total: {ts:.1f} MB downloaded"))
        progress_window.after(0, lambda: add_log(">>> Ready for next batch."))
        progress_window.after(0, lambda: close_btn.configure(text="[ ENTER ] CLOSE", fg_color=THEME_COLORS["accent"]))

    # Uruchom demo
    thread = threading.Thread(target=demo_download, daemon=True)
    thread.start()

    progress_window.mainloop()

# Uruchom
if __name__ == "__main__":
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")
    show_playlist_download_progress(test_videos)

