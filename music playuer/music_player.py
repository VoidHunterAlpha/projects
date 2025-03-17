import os
import tkinter as tk
from tkinter import filedialog, ttk
from mutagen.mp3 import MP3
import pygame
from PIL import Image, ImageTk
import io

class MusicPlayer:
    def __init__(self, root):
        self.root = root
        self.root.title("Sleek Music Player")
        self.root.geometry("400x650")
        self.root.configure(bg="#282C34")
        
        pygame.init()
        pygame.mixer.init()
        self.MUSIC_END = pygame.USEREVENT + 1
        pygame.mixer.music.set_endevent(self.MUSIC_END)

        self.playlist = []
        self.current_index = 0
        self.paused = False
        self.seeking = False
        self.total_length = 0

        self.album_art = tk.Label(root, bg="#282C34")
        self.album_art.pack(pady=20)

        self.song_label = tk.Label(root, text="No Song Loaded", font=("Helvetica", 16), fg="#FFFFFF", bg="#282C34", wraplength=350)
        self.song_label.pack(pady=10)

        self.progress_bar = ttk.Scale(root, from_=0, to=100, orient="horizontal", length=300, command=self.set_position)
        self.progress_bar.pack(pady=10)

        # Time labels
        time_frame = tk.Frame(root, bg="#282C34")
        time_frame.pack(pady=5)
        
        self.current_time_label = tk.Label(time_frame, text="00:00", fg="#FFFFFF", bg="#282C34")
        self.current_time_label.pack(side=tk.LEFT)
        
        self.total_time_label = tk.Label(time_frame, text="00:00", fg="#FFFFFF", bg="#282C34")
        self.total_time_label.pack(side=tk.RIGHT)

        self.volume_slider = ttk.Scale(root, from_=0, to=1, orient="horizontal", length=300, command=self.set_volume)
        self.volume_slider.set(0.5)
        self.volume_slider.pack(pady=10)

        button_frame = tk.Frame(root, bg="#282C34")
        button_frame.pack(pady=20)

        # Use Pillow to load icons (replace with actual paths)
        self.play_icon = ImageTk.PhotoImage(Image.new("RGB", (50, 50), "#61AFEF"))
        self.pause_icon = ImageTk.PhotoImage(Image.new("RGB", (50, 50), "#E06C75"))
        self.next_icon = ImageTk.PhotoImage(Image.new("RGB", (50, 50), "#98C379"))
        self.prev_icon = ImageTk.PhotoImage(Image.new("RGB", (50, 50), "#D19A66"))

        self.play_button = tk.Button(button_frame, image=self.play_icon, command=self.play_music, bg="#61AFEF", width=50, height=50)
        self.play_button.grid(row=0, column=0, padx=5)

        self.pause_button = tk.Button(button_frame, image=self.pause_icon, command=self.pause_music, bg="#E06C75", width=50, height=50)
        self.pause_button.grid(row=0, column=1, padx=5)

        self.next_button = tk.Button(button_frame, image=self.next_icon, command=self.next_music, bg="#98C379", width=50, height=50)
        self.next_button.grid(row=0, column=2, padx=5)

        self.prev_button = tk.Button(button_frame, image=self.prev_icon, command=self.prev_music, bg="#D19A66", width=50, height=50)
        self.prev_button.grid(row=0, column=3, padx=5)

        self.load_button = tk.Button(root, text="Load Music Folder", command=self.load_music_folder, bg="#C678DD", fg="#FFFFFF", width=20)
        self.load_button.pack(pady=20)

        # Progress bar bindings
        self.progress_bar.bind("<ButtonPress-1>", self.start_seek)
        self.progress_bar.bind("<ButtonRelease-1>", self.end_seek)

        # Start update loop
        self.root.after(100, self.update_time)

    def format_time(self, seconds):
        minutes = int(seconds // 60)
        seconds = int(seconds % 60)
        return f"{minutes:02}:{seconds:02}"

    def load_music_folder(self):
        folder_path = filedialog.askdirectory(title="Select Music Folder")
        if folder_path:
            self.playlist = self.get_mp3_files_in_folder(folder_path)
            if self.playlist:
                self.current_index = 0
                self.display_song()

    def get_mp3_files_in_folder(self, folder_path):
        mp3_files = []
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                if file.lower().endswith(".mp3"):
                    mp3_files.append(os.path.join(root, file))
        return mp3_files

    def display_song(self):
        song_path = self.playlist[self.current_index]
        audio = MP3(song_path)
        self.total_length = audio.info.length
        song_name = os.path.basename(song_path)
        self.song_label.config(text=song_name)
        self.progress_bar.config(to=self.total_length)
        self.total_time_label.config(text=self.format_time(self.total_length))
        self.current_time_label.config(text="00:00")
        self.display_album_art(song_path)

    def display_album_art(self, song_path):
        try:
            audio = MP3(song_path)
            if 'APIC:' in audio.tags:
                image_data = audio.tags['APIC:'].data
                image = Image.open(io.BytesIO(image_data)).resize((200, 200))
                photo = ImageTk.PhotoImage(image)
                self.album_art.config(image=photo)
                self.album_art.image = photo
            else:
                self.album_art.config(image='')
        except Exception as e:
            self.album_art.config(image='')

    def play_music(self):
        if self.playlist:
            if self.paused:
                pygame.mixer.music.unpause()
                self.paused = False
            else:
                pygame.mixer.music.load(self.playlist[self.current_index])
                pygame.mixer.music.play()
                self.paused = False

    def pause_music(self):
        if self.playlist and pygame.mixer.music.get_busy():
            pygame.mixer.music.pause()
            self.paused = True

    def next_music(self):
        if self.current_index < len(self.playlist) - 1:
            self.current_index += 1
            self.paused = False
            self.play_music()
            self.display_song()

    def prev_music(self):
        if self.current_index > 0:
            self.current_index -= 1
            self.paused = False
            self.play_music()
            self.display_song()

    def set_volume(self, value):
        pygame.mixer.music.set_volume(float(value))

    def start_seek(self, event):
        self.seeking = True

    def end_seek(self, event):
        if self.playlist:
            seek_position = self.progress_bar.get()
            pygame.mixer.music.stop()
            pygame.mixer.music.load(self.playlist[self.current_index])
            pygame.mixer.music.play(start=seek_position)
            self.seeking = False

    def set_position(self, value):
        if self.playlist and not self.paused and not self.seeking:
            self.progress_bar.set(float(value))

    def update_time(self):
        # Check for music end event
        for event in pygame.event.get():
            if event.type == self.MUSIC_END:
                self.next_music()

        # Update current time
        if self.playlist:
            current_pos = pygame.mixer.music.get_pos() / 1000
            if current_pos < 0:
                current_pos = 0
            
            self.current_time_label.config(text=self.format_time(current_pos))
            
            if not self.seeking:
                self.progress_bar.set(current_pos)

        self.root.after(100, self.update_time)

if __name__ == "__main__":
    root = tk.Tk()
    app = MusicPlayer(root)
    root.mainloop()