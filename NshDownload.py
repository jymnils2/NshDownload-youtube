import customtkinter
import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
from pytubefix import YouTube
from pytubefix.cli import on_progress
import os
import re
from threading import *
import platform
import getpass
import time
import sys
import shutil
import subprocess

# Limpiar consola según el sistema
os.system("cls" if platform.system() == "Windows" else "clear")

def get_resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)

# Localizar FFmpeg
ffmpeg_exe = shutil.which("ffmpeg")
if not ffmpeg_exe:
    name = "ffmpeg.exe" if platform.system() == "Windows" else "ffmpeg"
    ffmpeg_exe = get_resource_path(name)
    if not ffmpeg_exe or not os.path.exists(ffmpeg_exe):
        ffmpeg_exe = None 

# Carpeta de descargas
download_folder = os.path.join(os.path.expanduser("~"), "Downloads", "NshDownload")
os.makedirs(download_folder, exist_ok=True)

class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()
        self.is_running = True
        self.geometry("500x500")
        self.title("NshDownload - Corregido")
        customtkinter.set_appearance_mode("dark")
        customtkinter.set_default_color_theme("blue")
        self.resizable(0,0)

        self.mytab = customtkinter.CTkTabview(self, width=450, height=480, corner_radius=15)
        self.mytab.pack(pady=(10,0))

        self.tab_1 = self.mytab.add("Home")
        self.tab_2 = self.mytab.add("About")

        self.label_video_text = customtkinter.CTkLabel(self.tab_1, text=f"Welcome {getpass.getuser()}", font=("Arial",19), wraplength=400, height=100)
        self.label_video_text.pack()

        self.progressbar = customtkinter.CTkProgressBar(self.tab_1)
        self.progressbar.pack(pady=(10,0))
        self.progressbar.configure(mode="determinate")
        self.progressbar.set(0)

        self.entry_url = customtkinter.CTkEntry(self.tab_1, placeholder_text="Enter an URL", width=250, border_width=1, height=35)
        self.entry_url.pack(pady=(30,0))

        self.optionmenu = customtkinter.CTkOptionMenu(self.tab_1, values=["360p", "480p","720p", "1080p"], width=140, height=35, corner_radius=10)
        self.optionmenu.pack(pady = (30,0) , padx = (0,95))
        self.optionmenu.set("720p")

        self.clear_url_button = customtkinter.CTkButton(self.tab_1, text="Clear Input", fg_color="#C40C0C", font=("arial",16), command=self.clear_url)
        self.clear_url_button.pack(pady=(30,0), padx = (120,0))

        self.download_button = customtkinter.CTkButton(self.tab_1, text="Download Video", fg_color="#839705", font=("arial",16), command=self.download_button_clicked)
        self.download_button.pack(pady=(30,0), padx = (120,0))

        about_text = ("DISCLAIMER & ABOUT\n\nDesarrollado para fines educativos.\nUsa FFmpeg para unir audio y video.")
        self.label_about = customtkinter.CTkLabel(self.tab_2, text=about_text, font=("Arial", 14), wraplength=400, justify="left")
        self.label_about.pack(pady=20, padx=20)
            
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    def cleanup_temp_files(self):
        for f in [getattr(self, 'video_input', None), getattr(self, 'sound_input', None)]:
            if f and os.path.exists(f):
                try: os.remove(f)
                except: pass

    def on_closing(self):
        if self.download_button.cget("state") == "disabled":
            if tk.messagebox.askokcancel("Exit", "Download in progress. Quit anyway?"):
                self.is_running = False
                self.destroy()
        else:
            self.destroy()

    def clear_url(self):
        self.entry_url.delete(0, tk.END)

    def download_button_clicked(self):
        self.download_button.configure(state="disabled")
        Thread(target=self.video_download, daemon=True).start()

    def progress_(self, stream, chunk, bytes_remaining):
        if not self.is_running: return
        total_size = stream.filesize
        bytes_downloaded = total_size - bytes_remaining
        self.after(0, lambda: self.progressbar.set(bytes_downloaded / total_size))

    def video_download(self):
        try:
            if not ffmpeg_exe:
                self.after(0, lambda: self.label_video_text.configure(text="FFmpeg not found in folder!"))
                return

            self.after(0, lambda: self.progressbar.set(0))
            url = self.entry_url.get()
            selected_res = self.optionmenu.get()
            yt = YouTube(url, on_progress_callback=self.progress_)
            
            # 1. Descargar Video (solo video)
            video = yt.streams.filter(only_video=True, file_extension="mp4", res=selected_res).first()
            if not video:
                self.after(0, lambda: self.label_video_text.configure(text=f"Resolution {selected_res} not available"))
                return

            video_title = re.sub(r'[\\/*?:"<>|]', "", yt.title)
            self.after(0, lambda: self.label_video_text.configure(text=f"Downloading: {video_title}"))

            self.video_input = os.path.join(download_folder, "temp_video.mp4")
            self.sound_input = os.path.join(download_folder, "temp_sound.m4a")
            self.target_path = os.path.join(download_folder, f"{video_title}_{selected_res}.mp4")

            video.download(output_path=download_folder, filename="temp_video.mp4")

            # 2. Descargar Audio
            audio = yt.streams.filter(only_audio=True).first()
            audio.download(output_path=download_folder, filename="temp_sound.m4a")

            # 3. Unir con FFmpeg usando subprocess (seguro para rutas con espacios)
            self.after(0, lambda: self.label_video_text.configure(text="Merging Audio and Video..."))
            
            cmd = [
                ffmpeg_exe, '-i', self.video_input, '-i', self.sound_input,
                '-c', 'copy', self.target_path, '-y', '-loglevel', 'quiet'
            ]
            
            result = subprocess.run(cmd, capture_output=True)

            if result.returncode == 0:
                if os.path.exists(self.video_input): os.remove(self.video_input)
                if os.path.exists(self.sound_input): os.remove(self.sound_input)
                self.after(0, lambda: self.label_video_text.configure(text="Download Complete!"))
            else:
                self.after(0, lambda: self.label_video_text.configure(text="FFmpeg Error. Files kept separately."))

        except Exception as e:
            self.after(0, lambda: self.label_video_text.configure(text="Error occurred. Check console."))
            print(f"Error: {e}")
        finally:
            self.after(0, lambda: self.download_button.configure(state="normal"))

if __name__ == "__main__":
    root = App()
    root.mainloop()
