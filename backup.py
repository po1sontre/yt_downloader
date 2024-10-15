import tkinter as tk
import customtkinter as ctk
import yt_dlp
from PIL import Image, ImageTk
import requests
from io import BytesIO
import threading
import queue
from tkinter import filedialog

class YouTubeDownloaderApp:
    def __init__(self, master):
        self.master = master
        self.master.title("YouTube Downloader")
        self.master.geometry("400x750")
        self.master.resizable(True, True)  # Allow resizing

        # Set the appearance mode and color theme
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # Input URL
        self.url_label = ctk.CTkLabel(master, text="Enter YouTube URL:")
        self.url_label.pack(pady=10, fill="x")

        self.url_entry = ctk.CTkEntry(master, placeholder_text="https://www.youtube.com/watch?v=...")
        self.url_entry.pack(pady=5, padx=20, fill="x")

        # Video Title Display
        self.title_label = ctk.CTkLabel(master, text="Video Title:")
        self.title_label.pack(pady=10, fill="x")

        self.title_display = ctk.CTkLabel(master, text="")
        self.title_display.pack(pady=5, fill="x")

        # Quality Selector
        self.quality_label = ctk.CTkLabel(master, text="Select Quality:")
        self.quality_label.pack(pady=10, fill="x")

        self.quality_combo = ctk.CTkComboBox(master, values=[], width=200)
        self.quality_combo.pack(pady=5)

        # File Format Options
        self.format_label = ctk.CTkLabel(master, text="Select File Format:")
        self.format_label.pack(pady=10, fill="x")

        self.format_combo = ctk.CTkComboBox(master, values=["mp4", "mp3"], width=200)
        self.format_combo.pack(pady=5)

        # Thumbnail Preview
        self.thumbnail_label = ctk.CTkLabel(master, text="Thumbnail Preview:")
        self.thumbnail_label.pack(pady=10, fill="x")

        self.thumbnail_display = ctk.CTkLabel(master)
        self.thumbnail_display.pack(pady=5)

        # Fetch Info Button
        self.fetch_info_button = ctk.CTkButton(master, text="Fetch Info", command=self.fetch_info)
        self.fetch_info_button.pack(pady=10)

        # Download Path
        self.download_path_label = ctk.CTkLabel(master, text="Download Path:")
        self.download_path_label.pack(pady=10, fill="x")

        self.download_path_entry = ctk.CTkEntry(master, placeholder_text="Select Download Directory...", state="disabled")
        self.download_path_entry.pack(pady=5, padx=20, fill="x")

        self.browse_button = ctk.CTkButton(master, text="Browse", command=self.select_download_path)
        self.browse_button.pack(pady=10)

        # Download Button
        self.download_button = ctk.CTkButton(master, text="Download", command=self.start_download)
        self.download_button.pack(pady=10)

        # Status Label
        self.status_label = ctk.CTkLabel(master, text="")
        self.status_label.pack(pady=10, fill="x")

        # Queue for thread communication
        self.queue = queue.Queue()
        self.master.after(100, self.process_queue)

        # Initialize download path
        self.download_path = ""

    def fetch_info(self):
        url = self.url_entry.get()
        ydl_opts = {
            'format': 'best',
            'noplaylist': True,
            'quiet': True
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            try:
                info = ydl.extract_info(url, download=False)
                video_title = info.get('title', 'Unknown Title')
                thumbnail_url = info.get('thumbnail', '')

                self.title_display.configure(text=video_title)

                if thumbnail_url:
                    self.set_thumbnail(thumbnail_url)
                else:
                    self.thumbnail_display.configure(image='', text='')

                available_qualities = set()
                for fmt in info.get('formats', []):
                    height = fmt.get('height')
                    if height:
                        available_qualities.add(height)

                unique_quality_options = sorted(list(available_qualities), reverse=True)
                string_quality_options = [str(height) for height in unique_quality_options]

                self.quality_combo.configure(values=string_quality_options)

                if string_quality_options:
                    self.quality_combo.set(string_quality_options[0])
                else:
                    self.quality_combo.set('')

                self.update_status("Info fetched successfully.", "green")
            except Exception as e:
                self.update_status(f"Error: {str(e)}", "red")

    def set_thumbnail(self, url):
        try:
            response = requests.get(url)
            response.raise_for_status()
            img_data = response.content
            img = Image.open(BytesIO(img_data))
            img = img.resize((120, 90), Image.LANCZOS)
            img_tk = ImageTk.PhotoImage(img)
            self.thumbnail_display.configure(image=img_tk)
            self.thumbnail_display.image = img_tk
        except requests.HTTPError:
            self.thumbnail_display.configure(image='', text='')  # Clear the image if none is available
        except Exception:
            self.thumbnail_display.configure(image='', text='')  # Clear the image if an error occurs

    def start_download(self):
        # Run the download_video method in a separate thread
        download_thread = threading.Thread(target=self.download_video)
        download_thread.start()

    def download_video(self):
        url = self.url_entry.get()
        selected_quality = self.quality_combo.get()
        selected_format = self.format_combo.get()

        if not self.download_path:
            self.queue.put(("Please select a download path.", "red"))
            return

        if selected_quality:
            height = int(selected_quality)
            if selected_format == 'mp4':
                ydl_opts = {
                    'format': f'bestvideo[height<={height}][ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]',
                    'outtmpl': f'{self.download_path}/%(title)s.%(ext)s',  # Use the selected download path
                    'noplaylist': True,
                }
            elif selected_format == 'mp3':
                ydl_opts = {
                    'format': 'bestaudio/best',
                    'extractaudio': True,
                    'audioformat': 'mp3',
                    'outtmpl': f'{self.download_path}/%(title)s.%(ext)s',  # Use the selected download path
                    'noplaylist': True,
                }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                try:
                    ydl.download([url])
                    self.queue.put(("Download completed!", "green"))
                except Exception as e:
                    self.queue.put((f"Error: {str(e)}", "red"))
        else:
            self.queue.put(("Please select a quality option.", "red"))

    def select_download_path(self):
        self.download_path = filedialog.askdirectory()
        if self.download_path:
            self.download_path_entry.configure(state="normal")
            self.download_path_entry.delete(0, tk.END)
            self.download_path_entry.insert(0, self.download_path)
            self.download_path_entry.configure(state="disabled")

    def update_status(self, message, color):
        # Update the status label in the main thread
        self.queue.put((message, color))

    def process_queue(self):
        try:
            message, color = self.queue.get_nowait()
            self.status_label.configure(text=message, text_color=color)
        except queue.Empty:
            pass
        self.master.after(100, self.process_queue)

if __name__ == "__main__":
    root = ctk.CTk()
    app = YouTubeDownloaderApp(root)
    root.mainloop()
