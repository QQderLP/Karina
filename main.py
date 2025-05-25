import tkinter as tk
from tkinter import messagebox, filedialog
import threading
import yt_dlp
import tkinter.ttk as ttk
import os
import time

class DownloaderApp:
    def __init__(self, root):
        self.root = root
        root.title("影片下載器")
        root.geometry("700x220")

        # 設定視窗圖示
        icon_path = "black-music-note-icon-6.ico"
        if os.path.exists(icon_path):
            root.iconbitmap(icon_path)
        else:
            print(f"警告：找不到圖示檔 {icon_path}")

        tk.Label(root, text="貼上影片網址:").grid(row=0, column=0, padx=5, pady=5, sticky='e')
        self.url_entry = tk.Entry(root, width=50)
        self.url_entry.grid(row=0, column=1, columnspan=3, padx=5, pady=5, sticky='w')

        tk.Label(root, text="輸出資料夾:").grid(row=1, column=0, padx=5, pady=5, sticky='e')
        self.output_path_var = tk.StringVar()
        self.output_path_label = tk.Label(root, textvariable=self.output_path_var, relief="sunken", width=40, anchor='w')
        self.output_path_label.grid(row=1, column=1, columnspan=2, padx=5, pady=5, sticky='w')
        self.browse_btn = tk.Button(root, text="選擇資料夾", command=self.browse_folder)
        self.browse_btn.grid(row=1, column=3, padx=5, pady=5)

        self.video_var = tk.BooleanVar(value=True)
        self.audio_var = tk.BooleanVar(value=True)
        tk.Checkbutton(root, text="下載影片", variable=self.video_var).grid(row=2, column=1, sticky='w', padx=5)
        tk.Checkbutton(root, text="下載音訊", variable=self.audio_var).grid(row=2, column=2, sticky='w', padx=5)

        self.download_btn = tk.Button(root, text="下載", command=self.start_download)
        self.download_btn.grid(row=2, column=3, padx=5, pady=5)

        self.pause_btn = tk.Button(root, text="暫停", state='disabled', command=self.toggle_pause)
        self.pause_btn.grid(row=2, column=4, padx=5, pady=5)

        self.progress_var = tk.DoubleVar()
        style = ttk.Style()
        style.theme_use('default')
        style.configure('green.Horizontal.TProgressbar', troughcolor='white', background='green')
        self.progress = ttk.Progressbar(root, maximum=100, variable=self.progress_var, length=500, style='green.Horizontal.TProgressbar')
        self.progress.grid(row=3, column=0, columnspan=5, padx=10, pady=15)
        self.progress_label = tk.Label(root, text="進度: 0%")
        self.progress_label.grid(row=4, column=0, columnspan=5)

        self.is_paused = False
        self.is_downloading = False
        self.download_thread = None

    def browse_folder(self):
        folder_selected = filedialog.askdirectory()
        if folder_selected:
            self.output_path_var.set(folder_selected)

    def start_download(self):
        url = self.url_entry.get().strip()
        output_path = self.output_path_var.get()
        if not url:
            messagebox.showwarning("警告", "請輸入影片網址")
            return
        if not output_path:
            messagebox.showwarning("警告", "請選擇輸出資料夾")
            return
        if self.is_downloading:
            messagebox.showinfo("訊息", "正在下載中，請稍候")
            return
        if not self.video_var.get() and not self.audio_var.get():
            messagebox.showwarning("警告", "請至少選擇下載影片或音訊")
            return

        self.is_downloading = True
        self.pause_btn.config(state='normal', text='暫停')
        self.is_paused = False
        self.progress_var.set(0)
        self.progress_label.config(text="進度: 0%")

        self.download_thread = threading.Thread(target=self.download_task, args=(url, output_path, self.video_var.get(), self.audio_var.get()))
        self.download_thread.start()

    def download_task(self, url, output_path, download_video, download_audio):
        ffmpeg_path = os.path.join(os.path.dirname(__file__), "ffmpeg.exe")

        ydl_opts = {
            'ffmpeg_location': ffmpeg_path,
            'outtmpl': os.path.join(output_path, '%(title)s.%(ext)s'),
            'progress_hooks': [self.progress_hook],
            'quiet': True,
        }

        # 設定格式
        if download_video and not download_audio:
            ydl_opts['format'] = 'bestvideo+bestaudio/bestvideo'
        elif not download_video and download_audio:
            ydl_opts['format'] = 'bestaudio/best'
        else:
            ydl_opts['format'] = 'bestvideo+bestaudio/best'

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            self.root.after(0, lambda: messagebox.showinfo("完成", "下載完成！"))
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("錯誤", f"下載失敗：{e}"))
        finally:
            self.is_downloading = False
            self.root.after(0, lambda: self.pause_btn.config(state='disabled'))
            self.root.after(0, lambda: self.progress_var.set(0))
            self.root.after(0, lambda: self.progress_label.config(text="進度: 0%"))

    def progress_hook(self, d):
        if d['status'] == 'downloading':
            if self.is_paused:
                while self.is_paused:
                    time.sleep(0.1)
            total_bytes = d.get('total_bytes') or d.get('total_bytes_estimate') or 1
            downloaded_bytes = d.get('downloaded_bytes', 0)
            percent = downloaded_bytes / total_bytes * 100
            self.root.after(0, lambda: self.progress_var.set(percent))
            self.root.after(0, lambda: self.progress_label.config(text=f"進度: {percent:.1f}%"))

    def toggle_pause(self):
        self.is_paused = not self.is_paused
        self.pause_btn.config(text="繼續" if self.is_paused else "暫停")

if __name__ == "__main__":
    root = tk.Tk()
    app = DownloaderApp(root)
    root.mainloop()
