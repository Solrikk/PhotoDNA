# gui.py
import tkinter as tk
from tkinter import messagebox, ttk
from vk_utils import process_images

def start_processing(album_url):
    if not album_url:
        messagebox.showwarning("Внимание", "Пожалуйста, введите ссылку на альбом или фотографию ВКонтакте.")
        return
    process_images(album_url)

def create_gui():
    root = tk.Tk()
    root.title("PhotoDNA - Анализ схожих изображений")
    root.geometry("900x500")
    root.configure(bg="#f0f2f5")
    root.resizable(False, False)

    style = ttk.Style()
    style.theme_use('default')
    style.configure("TLabel", font=("Segoe UI", 12), background="#f0f2f5")
    style.configure("TEntry", font=("Segoe UI", 11))
    style.configure("TButton", font=("Segoe UI", 11, "bold"), padding=10, background="#0066cc")
    style.configure("Header.TLabel", font=("Segoe UI", 24, "bold"), foreground="#1a1a1a", background="#f0f2f5")
    style.configure("Main.TFrame", background="#f0f2f5")
    style.configure("Blue.Horizontal.TProgressbar", background="#0066cc", troughcolor="#e6e6e6")

    main_frame = ttk.Frame(root, padding=30, style="Main.TFrame")
    main_frame.pack(fill=tk.BOTH, expand=True)

    header = ttk.Label(main_frame, text="PhotoDNA", style="Header.TLabel")
    header.pack(pady=(0, 5))

    subheader = ttk.Label(main_frame, text="Умный поиск и анализ изображений", font=("Segoe UI", 12), background="#f0f2f5", foreground="#666666")
    subheader.pack(pady=(0, 20))

    input_frame = ttk.Frame(main_frame, style="Main.TFrame")
    input_frame.pack(fill=tk.X, pady=10)

    label = ttk.Label(input_frame, text="Введите ссылку на альбом или фотографию:", font=("Segoe UI", 11))
    label.pack(pady=(0, 8))

    entry = ttk.Entry(input_frame, width=80, font=("Segoe UI", 11))
    entry.pack(pady=(0, 5))

    def show_context_menu(event):
        context_menu.tk_popup(event.x_root, event.y_root)

    context_menu = tk.Menu(root, tearoff=0)
    context_menu.add_command(label="Вставить", command=lambda: entry.event_generate("<<Paste>>"))
    context_menu.add_command(label="Копировать", command=lambda: entry.event_generate("<<Copy>>"))
    entry.bind("<Button-3>", show_context_menu)

    progress_frame = ttk.Frame(main_frame, style="Main.TFrame")
    progress_frame.pack(fill=tk.X, pady=15)

    progress = ttk.Progressbar(progress_frame, orient=tk.HORIZONTAL, length=700, mode='indeterminate', style="Blue.Horizontal.TProgressbar")
    progress.pack()

    def on_start():
        album_url = entry.get().strip()
        if album_url:
            start_button.configure(state='disabled')
            progress.start()
            root.update_idletasks()
            start_processing(album_url)
            progress.stop()
            start_button.configure(state='normal')
        else:
            messagebox.showwarning("PhotoDNA", "Пожалуйста, введите ссылку на альбом или фотографию.")

    def paste(event):
        try:
            entry.event_generate("<<Paste>>")
        except:
            pass

    entry.bind("<Control-v>", paste)
    entry.bind("<Command-v>", paste)

    start_button = ttk.Button(main_frame, text="Начать обработку", command=on_start)
    start_button.pack(pady=20)

    root.mainloop()
