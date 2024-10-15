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
        self.master.geometry("400x800")
        self.master.resizable(True, True)

        # Set the appearance mode and color theme
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # Load and set the icon using wm_iconphoto (requires PNG)
        icon_image = ImageTk.PhotoImage(file=r"C:\Users\Gaming\Desktop\po1sontre\coding stuff\PERSONAL\(complete)youtubedown\icon.png")
        self.master.wm_iconphoto(True, icon_image)

        # Input URL
        self.url_label = ctk.CTkLabel(master, text="Enter YouTube URL:")
        self.url_label.pack(pady=(10, 0))

        self.url_entry = ctk.CTkEntry(master, placeholder_text="https://www.youtube.com/watch?v=...")
        self.url_entry.pack(pady=5, padx=20, fill="x")

        # Video Title Display
        self.title_label = ctk.CTkLabel(master, text="Video Title:")
        self.title_label.pack(pady=(10, 0))

        self.title_display = ctk.CTkLabel(master, text="")
        self.title_display.pack(pady=5)

        # Quality Selector
        self.quality_label = ctk.CTkLabel(master, text="Select Quality:")
        self.quality_label.pack(pady=(10, 0))

        self.quality_combo = ctk.CTkComboBox(master, values=[], width=200)
        self.quality_combo.pack(pady=5)

        # File Format Options
        self.format_label = ctk.CTkLabel(master, text="Select File Format:")
        self.format_label.pack(pady=(10, 0))

        self.format_combo = ctk.CTkComboBox(master, values=["mp4", "mp3"], width=200)
        self.format_combo.pack(pady=5)

        # Thumbnail Preview
        self.thumbnail_label = ctk.CTkLabel(master, text="Thumbnail Preview:")
        self.thumbnail_label.pack(pady=(10, 0))

        self.thumbnail_display = ctk.CTkLabel(master)
        self.thumbnail_display.pack(pady=5)

        # Fetch Info Button
        self.fetch_info_button = ctk.CTkButton(master, text="Fetch Info", command=self.fetch_info)
        self.fetch_info_button.pack(pady=10)

        # Download Path
        self.download_path_label = ctk.CTkLabel(master, text="Download Path:")
        self.download_path_label.pack(pady=(10, 0))

        self.download_path_entry = ctk.CTkEntry(master, placeholder_text="Select Download Directory...", state="disabled")
        self.download_path_entry.pack(pady=5, padx=20, fill="x")

        # Browse Button
        self.browse_button = ctk.CTkButton(master, text="Browse", command=self.select_download_path)
        self.browse_button.pack(pady=10)

        # Download Button
        self.download_button = ctk.CTkButton(master, text="Download", command=self.start_download)
        self.download_button.pack(pady=10)

        # Progress Bar
        self.progress_bar = ctk.CTkProgressBar(master)
        self.progress_bar.pack(pady=10, padx=20, fill="x")
        self.progress_bar.set(0)  # Initialize progress bar to 0

        # Credit Label
        self.credit_label = ctk.CTkLabel(master, text="Created by po1sontre", text_color="gray")
        self.credit_label.pack(pady=(0, 5))

        # Status Label
        self.status_label = ctk.CTkLabel(master, text="")
        self.status_label.pack(pady=10)

        # Queue for thread communication
        self.queue = queue.Queue()
        self.master.after(100, self.process_queue)

        # Initialize download path
        self.download_path = ""

    def fetch_info(self):
        url = self.url_entry.get()
        try:
            formats = self.fetch_available_formats(url)
            if formats:
                # Update the quality combo box with available formats
                quality_options = [f"{f[0]} - {f[2]} ({f[1]})" for f in formats]  # Format: ID - resolution (ext)
                self.quality_combo.configure(values=quality_options)

                # Set default selected quality
                self.quality_combo.set(quality_options[0])

                # Get video title
                ydl_opts = {'noplaylist': True, 'quiet': True}
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(url, download=False)
                    video_title = info.get('title', 'Unknown Title')
                    self.title_display.configure(text=video_title)

                # Fetch thumbnail
                thumbnail_url = info.get('thumbnail', '')
                if thumbnail_url:
                    self.set_thumbnail(thumbnail_url)
                else:
                    self.thumbnail_display.configure(image='', text='')

                self.update_status("Info fetched successfully.", "green")
            else:
                self.update_status("No formats available.", "red")
        except Exception as e:
            self.update_status(f"Error fetching info: {str(e)}", "red")

    def fetch_available_formats(self, url):
        """Fetch available video formats from a given URL."""
        try:
            with yt_dlp.YoutubeDL() as ydl:
                info_dict = ydl.extract_info(url, download=False)
                formats = info_dict.get('formats', [])
                return [(f['format_id'], f['ext'], f.get('height', 'audio only')) for f in formats]
        except Exception as e:
            print(f"Error fetching formats: {e}")
            return []

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
        except Exception as e:
            self.thumbnail_display.configure(image='', text='')  # Clear the image if an error occurs

    def start_download(self):
        # Run the download_video method in a separate thread
        download_thread = threading.Thread(target=self.download_video)
        download_thread.start()

    def download_video(self):
        url = self.url_entry.get()
        selected_quality = self.quality_combo.get().split(' - ')[0]  # Get only the format ID

        if not self.download_path:
            self.queue.put(("Please select a download path.", "red"))
            return

        try:
            ydl_opts = {
                'format': selected_quality,  # Use selected quality directly
                'outtmpl': f'{self.download_path}/%(title)s.%(ext)s',  # Use the selected download path
                'noplaylist': True,
                'progress_hooks': [self.progress_hook]  # Attach the progress hook
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
                self.queue.put(("Download completed!", "green"))

        except Exception as e:
            self.queue.put((f"Error during download: {str(e)}", "red"))

    def progress_hook(self, d):
        if d['status'] == 'downloading':
            downloaded_bytes = d.get('downloaded_bytes', 0)
            total_bytes = d.get('total_bytes', d.get('total_bytes_estimate', 1))  # Fallback to estimate if total is not available
            if total_bytes > 0:  # Prevent division by zero
                progress = downloaded_bytes / total_bytes
                self.queue.put(("Downloading...", "blue"))
                self.progress_bar.set(progress)
        elif d['status'] == 'finished':
            self.queue.put(("Download finished!", "green"))
            self.progress_bar.set(1.0)  # Set progress bar to full

    def select_download_path(self):
        self.download_path = filedialog.askdirectory()
        if self.download_path:
            self.download_path_entry.configure(state="normal")
            self.download_path_entry.delete(0, tk.END)
            self.download_path_entry.insert(0, self.download_path)
            self.download_path_entry.configure(state="disabled")
            self.update_status("Download path set.", "green")
        else:
            self.update_status("No path selected.", "red")

    def update_status(self, message, color):
        self.status_label.configure(text=message, text_color=color)

    def process_queue(self):
        try:
            while True:
                message, color = self.queue.get_nowait()
                self.update_status(message, color)
                self.queue.task_done()
        except queue.Empty:
            pass
        finally:
            self.master.after(100, self.process_queue)


if __name__ == "__main__":
    root = ctk.CTk()
    app = YouTubeDownloaderApp(root)
    root.mainloop()
