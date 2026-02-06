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
os.system("cls" if platform.system() == "Windows" else "clear")



def get_resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)

ffmpeg_exe = shutil.which("ffmpeg")


if not ffmpeg_exe:
    name = "ffmpeg.exe" if platform.system() == "Windows" else "ffmpeg"
    ffmpeg_exe = get_resource_path(name)
    if not ffmpeg_exe or not os.path.exists(ffmpeg_exe):
        ffmpeg_exe = None 

download_folder = os.path.join(os.path.expanduser("~"), "Downloads", "DownloadIt")
os.makedirs(download_folder, exist_ok=True)
class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()
        self.is_running = True
        self.geometry("500x500")
        self.title("DownloadIt")
        customtkinter.set_appearance_mode("dark")
        customtkinter.set_default_color_theme("blue")
        self.resizable(0,0)
        #self.img = tk.PhotoImage(file="images/starwarsS0E2.png")pack()
        #self.iconphoto(False,self.img)

        self.mytab = customtkinter.CTkTabview(self,
                                              width=450,
                                              height=480,
                                              corner_radius=15,)
        self.mytab.pack(pady=(10,0))

        self.tab_1 = self.mytab.add("Home")
        self.tab_2 = self.mytab.add("About")

        self.label_video_text = customtkinter.CTkLabel(self.tab_1,text=f"Welcome {getpass.getuser()}",font=("Arial",19),wraplength=400,height=100)
        self.label_video_text.pack()

        self.progressbar = customtkinter.CTkProgressBar(self.tab_1)
        self.progressbar.pack(pady=(10,0))
        self.progressbar.configure(mode="determinate")
        self.progressbar.set(0)
        self.entry_url = customtkinter.CTkEntry(self.tab_1,placeholder_text="Enter an URL",width=250,border_width=1,height=35)
        self.entry_url.pack(pady=(30,0))
        self.optionmenu = customtkinter.CTkOptionMenu(self.tab_1, values=["360p", "480p","720p"],
                                                      width=140,
                                                      height=35,
                                                    corner_radius=10,                                                     fg_color="#343638",    
                                                    button_color="#1f538d",
                                                    button_hover_color="#14375e",
                                                    text_color="white",
                                                    dropdown_fg_color="#2b2b2b", 
                                                    dropdown_hover_color="#3d3d3d",
                                                    dropdown_text_color="white",
                                                    font=("Inter", 13, "bold"))
        self.optionmenu.pack(pady = (30,0) , padx = (0,95))
        self.optionmenu.set("480p")
        self.clear_url_button = customtkinter.CTkButton(self.tab_1,text="Clear Input",fg_color="#C40C0C",font=("arial",16),command=self.clear_url,hover_color="#F63049")
        self.clear_url_button.pack(pady=(30,0),padx = (120,0))
        self.download_button = customtkinter.CTkButton(self.tab_1,text="Download Video",fg_color="#839705",font=("arial",16),hover_color="#75B06F",command=self.download_button_clicked)
        self.download_button.pack(pady=(30,0),padx = (120,0))
        self.label_info_creator = customtkinter.CTkLabel(self.tab_1,text="Product by Hasan Çabuk.",font=("Helvetica" , 10))
        self.label_info_creator.pack(pady = (38,0),padx=(0,300))
        about_text = (
    "DISCLAIMER & ABOUT\n\n"
    "This application has been developed strictly for EDUCATIONAL PURPOSES ONLY. "
    "The primary goal of this project is to demonstrate software engineering concepts "
    "such as multi-threading, GUI design, and external process management.\n\n"
    "Non-Commercial Use: This software is not intended for any commercial use. "
    "The developer does not host, store, or distribute any copyrighted content.\n\n"
    "User Responsibility: By using this software, you agree that the responsibility "
    "for any legal issues or copyright violations resulting from the use of this tool "
    "rests entirely with the user. Please respect YouTube's Terms of Service.\n\n"
    "Developed by: Hasan Cabuk")
        self.label_about = customtkinter.CTkLabel(
        self.tab_2, 
        text=about_text, 
        font=("Arial", 14), 
        wraplength=400, 
        justify="left")
        self.label_about.pack(pady=20, padx=20)
            

        









        self.protocol("WM_DELETE_WINDOW", self.on_closing)


    def cleanup_temp_files(self):
        files_to_clean = [
            getattr(self,'video_input',None),
            getattr(self,'sound_input',None)
        ]
        for dosya in files_to_clean:
            if dosya and os.path.exists(dosya):
                try:
                    os.remove(dosya)
                except Exception as e:
                    print(f"dosya silinemedi. {dosya} \nError {e}")

    def on_closing(self):
        if self.download_button.cget("state") == "disabled":
            if tk.messagebox.askokcancel("Exit", "Download is proccesing. Are you sure you want to close? \n(Incomplete files will be deleted)"):
                self.is_running = False
                self.cleanup_temp_files()
                time.sleep(3)
                self.destroy()
        else:
            self.destroy()
    def clear_url(self):
        self.after(0, lambda: self.entry_url.delete(0, tk.END))

    def download_button_clicked(self):
        self.download_button.configure(state = "disabled")
        t1 = Thread(target=self.video_download)
        t1.daemon = True
        t1.start()



    def progress_(self,stream, chunk, bytes_remaining):
        if not self.is_running:
            return
        total_size = stream.filesize
        bytes_downloaded = total_size - bytes_remaining
        percentage = (bytes_downloaded / total_size)
        self.after(0, lambda: self.progressbar.set(percentage))




    def video_download(self):
        try:
            if ffmpeg_exe is None:
                self.after(0,lambda: self.label_video_text.configure(text = "'ffmpeg' is not installed on your system.\n" \
                "Please install ffmpeg on your system and try again."))
                self.after(0, lambda: self.download_button.configure(state="normal"))
                return
            self.after(0,lambda: self.progressbar.set(0))
            selected_res = self.optionmenu.get()
            yt = YouTube(self.entry_url.get(), on_progress_callback= self.progress_)
            video = yt.streams.filter(only_video=True,file_extension="mp4",res=f"{selected_res}").first()
            if video is None:
                self.after(0,lambda: self.label_video_text.configure(text = f"The selected resolution ({selected_res}) is not available for this video"))
                self.after(0, lambda: self.download_button.configure(state="normal"))
                return
            self.video_input = os.path.join(download_folder, "video.mp4")
            self.sound_input = os.path.join(download_folder, "sound.m4a")
            video_title = re.sub(r'[\\/*?:"<>|]', "", video.title)
            self.after(0, lambda: self.label_video_text.configure(text=f"{video_title}\n{yt.author}"))
            video.download(output_path = download_folder,filename = "video.mp4")
            sound = yt.streams.filter(only_audio=True,).first()
            sound.download(output_path = download_folder,filename = "sound.m4a")
            self.target_path = os.path.join(download_folder, f"{video_title}({selected_res}).mp4")
            os.system(f'"{ffmpeg_exe}" -i "{self.video_input}" -i "{self.sound_input}" -c copy "{self.target_path}" -y -loglevel quiet')
            os.remove(f"{self.video_input}")
            os.remove(f"{self.sound_input}")
            time.sleep(1)
            self.after(0, lambda: self.label_video_text.configure(text=f"{video_title}\n{yt.author}\n Download Complete!"))
        except Exception as e:
            self.after(0,lambda: self.label_video_text.configure(text = "An error occurred. Please try again."))
            print(f"Error : {e}")
            self.clear_url()
        finally:
            self.after(0, lambda: self.download_button.configure(state="normal"))


                        





            
        
root = App()
root.mainloop()