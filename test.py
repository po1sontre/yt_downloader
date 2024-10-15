import os

result = os.system('ffmpeg -version')
print("FFmpeg accessible" if result == 0 else "FFmpeg not accessible")
import tkinter as tk
from tkinter import filedialog, ttk
import yt_dlp
from queue import Queue
import threading

class YouTubeDownloader:
    def __init__(self, master):
        self.master = master
        self.master.title("YouTube Video Downloader")
        self.download_path = ""
        self.queue = Queue()

        self.create_widgets()
        self.start_update_thread()

    def create_widgets(self):
        # URL Entry
        self.url_label = tk.Label(self.master, text="YouTube URL:")
        self.url_label.pack(pady=5)
        self.url_entry = tk.Entry(self.master, width=50)
        self.url_entry.pack(pady=5)

        # Quality Selection
        self.quality_label = tk.Label(self.master, text="Select Video Quality (e.g., 720p):")
        self.quality_label.pack(pady=5)
        self.quality_combo = ttk.Combobox(self.master, values=["144p", "240p", "360p", "480p", "720p", "1080p"])
        self.quality_combo.set("720p")
        self.quality_combo.pack(pady=5)

        # Format Selection
        self.format_label = tk.Label(self.master, text="Select Format:")
        self.format_label.pack(pady=5)
        self.format_combo = ttk.Combobox(self.master, values=["mp4", "mp3"])
        self.format_combo.set("mp4")
        self.format_combo.pack(pady=5)

        # Download Path Selection
        self.path_button = tk.Button(self.master, text="Select Download Path", command=self.select_download_path)
        self.path_button.pack(pady=5)

        # Download Button
        self.download_button = tk.Button(self.master, text="Download Video", command=self.download_video)
        self.download_button.pack(pady=5)

        # Status Display
        self.status_display = tk.Text(self.master, width=60, height=10, state='disabled')
        self.status_display.pack(pady=5)

    def start_update_thread(self):
        self.master.after(100, self.update_status)

    def update_status(self):
        while not self.queue.empty():
            message, color = self.queue.get()
            self.status_display.configure(state='normal')
            self.status_display.insert(tk.END, message + '\n')
            self.status_display.configure(state='disabled')
            self.status_display.see(tk.END)
        self.master.after(100, self.update_status)

    def select_download_path(self):
        self.download_path = filedialog.askdirectory()
        if self.download_path:
            self.queue.put((f"Download path set to: {self.download_path}", "blue"))

    def download_video(self):
        url = self.url_entry.get()
        selected_quality = self.quality_combo.get()  # Get quality directly
        selected_format = self.format_combo.get()

        if not self.download_path:
            self.queue.put(("Please select a download path.", "red"))
            return

        try:
            with yt_dlp.YoutubeDL({'noplaylist': True, 'quiet': True}) as ydl:
                # Extract video information without downloading
                info = ydl.extract_info(url, download=False)
                available_formats = info.get('formats', [])

                # Logic to find the desired format based on quality and type
                chosen_format = None
                for fmt in available_formats:
                    if selected_format == 'mp4' and fmt.get('ext') == 'mp4' and fmt.get('height') == int(selected_quality[:-1]):
                        chosen_format = fmt['format_id']
                        break
                    elif selected_format == 'mp3' and fmt.get('acodec') != 'none':
                        chosen_format = fmt['format_id']
                        break

                if not chosen_format:
                    self.queue.put(("No matching format found. Available formats:", "orange"))
                    for fmt in available_formats:
                        self.queue.put((f"{fmt['format_id']} ({fmt['resolution'] if 'height' in fmt else 'audio only'}) - {fmt['ext']}", "orange"))
                    return

                # Proceed to download with the chosen format
                ydl_opts = {
                    'format': chosen_format,
                    'outtmpl': f'{self.download_path}/%(title)s.%(ext)s',
                    'noplaylist': True,
                    'progress_hooks': [self.progress_hook]
                }

                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([url])
                    self.queue.put(("Download completed!", "green"))

        except Exception as e:
            self.queue.put((f"Error during download: {str(e)}", "red"))

    def progress_hook(self, d):
        if d['status'] == 'finished':
            self.queue.put((f"Finished downloading: {d['filename']}", "green"))

if __name__ == "__main__":
    root = tk.Tk()
    app = YouTubeDownloader(root)
    root.mainloop()
