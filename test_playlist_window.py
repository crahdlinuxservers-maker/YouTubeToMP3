"""
Test okna pobierania playlisty - tylko demo wizualne
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

# Dane testowe - symulacja zaznaczonych wideo
test_videos = [
    {'title': 'AC/DC - Back In Black (Official Video)', 'url': 'https://youtube.com/watch?v=test1'},
    {'title': 'Queen - Bohemian Rhapsody', 'url': 'https://youtube.com/watch?v=test2'},
    {'title': 'Led Zeppelin - Stairway To Heaven', 'url': 'https://youtube.com/watch?v=test3'},
    {'title': 'Pink Floyd - Comfortably Numb', 'url': 'https://youtube.com/watch?v=test4'},
    {'title': 'Guns N\' Roses - Sweet Child O\' Mine', 'url': 'https://youtube.com/watch?v=test5'},
]

def show_playlist_download_progress(selected_videos):
    """
    Okno postępu pobierania playlisty - DEMO
    """
    # Stwórz okno postępu
    progress_window = ctk.CTk()
    progress_window.title(f"📥 Pobieranie playlisty ({len(selected_videos)} wideo)")
    progress_window.geometry("800x700")
    progress_window.resizable(False, False)

    # Główny frame
    main_frame = CTkFrame(progress_window, fg_color=THEME_COLORS["primary"])
    main_frame.pack(fill="both", expand=True, padx=15, pady=15)

    # Nagłówek
    header_label = CTkLabel(
        main_frame,
        text=f"📥 Pobieranie {len(selected_videos)} wideo z playlisty",
        font=("Helvetica", 14, "bold"),
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
            font=("Helvetica", 10),
            text_color="#666666",
            anchor="center",
            width=200
        )
        mini_stats.pack(side="left", padx=2)

        # 3. Mini pasek (po prawej) - z odstępem 5 spacji
        mini_progress = CTkProgressBar(
            one_line_container,
            width=80,
            height=6,
            fg_color="#2a2a2a",
            progress_color="#ff8c00",
            corner_radius=2
        )
        mini_progress.pack(side="right", padx=(15, 0))  # 15px padding z lewej strony = ~5 spacji
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
        text="0 / 5 ukończone",
        font=("Helvetica", 11),
        text_color=THEME_COLORS["text_secondary"]
    )
    progress_count_label.pack(pady=(2, 10))


    # Przyciski kontroli
    control_frame = CTkFrame(main_frame, fg_color="transparent")
    control_frame.pack(fill="x")

    # Przycisk Zamknij (demo)
    cancel_btn = CTkButton(
        control_frame,
        text="✅ Zamknij (DEMO)",
        command=progress_window.destroy,
        height=35,
        font=("Helvetica", 12, "bold"),
        fg_color=THEME_COLORS["accent"],
        hover_color=THEME_COLORS["hover"]
    )
    cancel_btn.pack(pady=5)

    # Symulacja pobierania (DEMO)
    def demo_download():
        import random
        time.sleep(1)
        total_size = 0
        success_count = 0

        for i in range(1, len(selected_videos) + 1):
            current_idx = i  # Przechwytujemy wartość dla lambda
            video_title = selected_videos[i-1]['title']

            # Aktualizuj status globalny
            def update_status(idx=current_idx):
                global_status_label.configure(text=f"📥 Pobieranie {idx}/{len(selected_videos)}...")
            progress_window.after(0, update_status)


            # Animacja pojedynczego pliku
            file_size = random.uniform(8, 25)
            for percent in range(0, 101, 10):
                # Mini pasek w liście dla tego pliku
                if current_idx in mini_progress_bars:
                    def update_mini(idx=current_idx, p=percent):
                        mini_progress_bars[idx].set(p/100)
                    progress_window.after(0, update_mini)

                # Statystyki - oblicz wartości
                speed_val = 5 - percent/20
                eta_val = 60 - percent//2
                size_val = (percent * file_size / 100)


                # Aktualizuj mini statystyki dla tego pliku (w liście!)
                if current_idx in mini_stats_labels:
                    def update_mini_stats(idx=current_idx, s=speed_val, e=eta_val, sz=size_val):
                        mini_stats_labels[idx].configure(
                            text=f"⚡ {s:.2f} MB/s | ⏱️ 00:{e:02d} | 📦 {sz:.1f} MB",
                            text_color=THEME_COLORS["text_secondary"]
                        )
                    progress_window.after(0, update_mini_stats)

                time.sleep(0.1)

            # Po zakończeniu - mini pasek na 100%
            if current_idx in mini_progress_bars:
                def set_mini_complete(idx=current_idx, fs=file_size):
                    mini_progress_bars[idx].set(1.0)
                    mini_progress_bars[idx].configure(progress_color="#4caf50")  # Zielony
                    # Finalne statystyki
                    if idx in mini_stats_labels:
                        mini_stats_labels[idx].configure(
                            text=f"✅ {fs:.1f} MB | 100%",
                            text_color="#4caf50"
                        )
                progress_window.after(0, set_mini_complete)

            # Aktualizuj postęp globalny
            total_size += file_size
            success_count += 1

            def update_global(idx=current_idx):
                global_progress_bar.set(idx/len(selected_videos))
                progress_count_label.configure(text=f"{idx} / {len(selected_videos)} ukończone")
            progress_window.after(0, update_global)

            time.sleep(0.3)


        # Zakończono
        progress_window.after(0, lambda: global_status_label.configure(
            text=f"✅ Ukończono! Pobrano {success_count}/{len(selected_videos)} wideo",
            text_color=THEME_COLORS["success"]
        ))
        progress_window.after(0, lambda: global_progress_bar.set(1.0))
        progress_window.after(0, lambda: cancel_btn.configure(text="✅ Zamknij"))

    # Uruchom demo
    thread = threading.Thread(target=demo_download, daemon=True)
    thread.start()

    progress_window.mainloop()

# Uruchom okno
if __name__ == "__main__":
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")
    show_playlist_download_progress(test_videos)

