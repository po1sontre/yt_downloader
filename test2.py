import os
import tkinter as tk
from tkinter import messagebox, filedialog
from tkinter import ttk
import yt_dlp

def fetch_available_formats(url):
    """Fetch available video formats from a given URL."""
    try:
        with yt_dlp.YoutubeDL() as ydl:
            info_dict = ydl.extract_info(url, download=False)
            formats = info_dict.get('formats', [])
            return [(f['format_id'], f['ext'], f.get('resolution', 'audio only')) for f in formats]
    except Exception as e:
        print(f"Error fetching formats: {e}")
        return []

def download_video(url, format_id, output_dir):
    """Download video or audio based on selected format."""
    ydl_opts = {
        'format': format_id,
        'outtmpl': os.path.join(output_dir, '%(title)s.%(ext)s'),
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }] if format_id.startswith('a') else [],
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

def start_download():
    """Initiate the download process based on user input."""
    url = url_entry.get()
    format_id = format_selector.get().split(" ")[0]  # Get only the format_id
    output_dir = filedialog.askdirectory(title="Select Output Directory")

    if not url or not format_id or not output_dir:
        messagebox.showerror("Error", "Please provide all fields.")
        return

    print(f"Starting download for: {url}")
    print(f"Selected format: {format_id}")
    print(f"Output directory: {output_dir}")

    download_video(url, format_id, output_dir)
    messagebox.showinfo("Success", "Download completed successfully!")

def update_format_selector(event):
    """Update format selector options based on the provided URL."""
    url = url_entry.get()
    if url:
        formats = fetch_available_formats(url)
        format_selector['values'] = [f"{f[0]} ({f[1]}, {f[2]})" for f in formats]
        if formats:
            format_selector.current(0)  # Select the first format

# GUI Setup
root = tk.Tk()
root.title("YouTube Downloader")
root.geometry("400x300")
root.configure(bg="#2b2b2b")  # Dark mode background color

# URL Entry
url_label = tk.Label(root, text="YouTube URL:", bg="#2b2b2b", fg="white")
url_label.pack(pady=10)
url_entry = tk.Entry(root, width=50, bg="#3c3c3c", fg="white", insertbackground='white')
url_entry.pack(pady=5)

# Format Selector
format_label = tk.Label(root, text="Select Format:", bg="#2b2b2b", fg="white")
format_label.pack(pady=10)
format_selector = ttk.Combobox(root, width=50, state="readonly", background="#3c3c3c", foreground="white")
format_selector.pack(pady=5)

# Bind URL entry to update format options
url_entry.bind("<Return>", update_format_selector)

# Download Button
download_button = tk.Button(root, text="Download", command=start_download, bg="#4CAF50", fg="white")
download_button.pack(pady=20)

# Exit Button
exit_button = tk.Button(root, text="Exit", command=root.quit, bg="#f44336", fg="white")
exit_button.pack(pady=5)

# Run the GUI
root.mainloop()
