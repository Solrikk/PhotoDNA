import tkinter as tk
from tkinter import ttk, messagebox
import logging
from processing import process_images

def start_processing(url):
    if not url:
        messagebox.showwarning("Внимание", "Введите ссылку на альбом/фото")
        return
    process_images(url)

def create_gui():
    r = tk.Tk()
    r.title("PhotoDNA")
    r.geometry("900x500")
    r.configure(bg="#f0f2f5")
    r.resizable(False, False)

    s = ttk.Style()
    s.theme_use('default')
    s.configure("TLabel", font=("Segoe UI", 12), background="#f0f2f5")
    s.configure("TEntry", font=("Segoe UI", 11))
    s.configure("TButton", font=("Segoe UI", 11, "bold"), padding=10, background="#0066cc")
    s.configure("Header.TLabel", font=("Segoe UI", 24, "bold"), foreground="#1a1a1a", background="#f0f2f5")
    s.configure("Main.TFrame", background="#f0f2f5")
    s.configure("Blue.Horizontal.TProgressbar", background="#0066cc", troughcolor="#e6e6e6")

    mf = ttk.Frame(r, padding=30, style="Main.TFrame")
    mf.pack(fill=tk.BOTH, expand=True)

    h = ttk.Label(mf, text="PhotoDNA", style="Header.TLabel")
    h.pack(pady=(0, 5))

    sh = ttk.Label(mf, text="Умный поиск и анализ изображений", font=("Segoe UI", 12), background="#f0f2f5", foreground="#666666")
    sh.pack(pady=(0, 20))

    inf = ttk.Frame(mf, style="Main.TFrame")
    inf.pack(fill=tk.X, pady=10)

    lbl = ttk.Label(inf, text="Введите ссылку на альбом или фотографию:", font=("Segoe UI", 11))
    lbl.pack(pady=(0, 8))

    e = ttk.Entry(inf, width=80, font=("Segoe UI", 11))
    e.pack(pady=(0, 5))

    def show_context_menu(event):
        context_menu.tk_popup(event.x_root, event.y_root)

    context_menu = tk.Menu(r, tearoff=0)
    context_menu.add_command(label="Вставить", command=lambda: e.event_generate("<<Paste>>"))
    context_menu.add_command(label="Копировать", command=lambda: e.event_generate("<<Copy>>"))
    e.bind("<Button-3>", show_context_menu)

    pf = ttk.Frame(mf, style="Main.TFrame")
    pf.pack(fill=tk.X, pady=15)

    pb = ttk.Progressbar(pf, orient=tk.HORIZONTAL, length=700, mode='indeterminate', style="Blue.Horizontal.TProgressbar")
    pb.pack()

    def on_start():
        url = e.get().strip()
        if url:
            b.configure(state='disabled')
            pb.start()
            r.update_idletasks()
            start_processing(url)
            pb.stop()
            b.configure(state='normal')
        else:
            messagebox.showwarning("PhotoDNA", "Введите ссылку")

    b = ttk.Button(mf, text="Начать обработку", command=on_start)
    b.pack(pady=20)

    r.mainloop()
