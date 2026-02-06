# DownloadIt 📥

**DownloadIt** is a modern YouTube video downloader desktop application built with Python. This project was developed as a technical study to understand multi-threading, network stream handling, and media merging processes in a GUI environment.

## ⚠️ Disclaimer (Educational Purposes Only)

**Important:** This project is strictly for **educational purposes only**. It was created to demonstrate software engineering concepts such as:

- GUI development with `customtkinter`
- Asynchronous programming and multi-threading
- Dependency management and external process handling (FFmpeg)
- Regular expressions for string sanitization

The developer does not encourage or condone the unauthorized downloading of copyrighted material. Users are responsible for complying with YouTube's Terms of Service and local copyright laws.

## 🚀 Features

- **High-Quality Downloads:** Merges separate video and audio streams for the best possible resolution using FFmpeg
- **Modern UI:** A clean, dark-mode responsive interface using CustomTkinter
- **Multi-threaded Execution:** The interface remains responsive during the download and merging process
- **Smart Cleanup:** Automatically removes temporary files after a successful merge or unexpected exit

## 🛠️ Prerequisites

This application requires **FFmpeg** to merge high-resolution video and audio files.

### Installing FFmpeg:

**Linux (Debian/Ubuntu):**
```bash
sudo apt update && sudo apt install ffmpeg
```

**Windows:**
1. Download the build from [ffmpeg.org](https://ffmpeg.org)
2. Add the `bin` folder to your System PATH OR place `ffmpeg.exe` in the project root directory

## 📦 Setup & Usage

1. **Clone the repository:**
```bash
git clone https://github.com/hasancabuk/downloadit.git
cd downloadit
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Run the application:**
```bash
python main.py
```

---

**Developed by:** Hasan Çabuk
