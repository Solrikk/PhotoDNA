import tkinter as tk
from tkinter import messagebox, filedialog, ttk
import logging
from datetime import datetime
from processing import process_images, cleanup_temp_files

RESULTS_FILE = 'results.xlsx'

def start_processing(album_url):
    if not album_url:
        messagebox.showwarning(
            "Внимание",
            "Пожалуйста, введите ссылку на альбом или фотографию ВКонтакте.")
        return

    if not (album_url.startswith('https://vk.com/album')
            or album_url.startswith('https://vk.com/photo')):
        messagebox.showwarning(
            "Ошибка",
            "Неверный формат ссылки. Используйте ссылку на альбом или фотографию ВКонтакте."
        )
        return

    try:
        process_images(album_url, None, None)
    except Exception as e:
        logging.error(f"Критическая ошибка при обработке: {str(e)}")
        messagebox.showerror("Ошибка",
                             "Произошла ошибка при обработке изображений")
        cleanup_temp_files()


def create_gui():
    root = tk.Tk()
    root.title("PhotoDNA - Анализ схожих изображений")
    root.geometry("800x700")
    root.configure(bg="#1a1b26")

    # Создаем список для хранения ссылок
    urls_list = []

    def add_url():
        url = entry.get().strip()
        if url:
            urls_list.append(url)
            urls_listbox.insert(tk.END, url)
            entry.delete(0, tk.END)

    def remove_url():
        selection = urls_listbox.curselection()
        if selection:
            index = selection[0]
            urls_list.pop(index)
            urls_listbox.delete(index)

    def process_all_urls():
        if not urls_list:
            messagebox.showwarning("PhotoDNA", "Добавьте хотя бы одну ссылку")
            return

        vk_login = login_entry.get().strip()
        vk_password = password_entry.get().strip()

        if not vk_login or not vk_password:
            messagebox.showwarning("PhotoDNA",
                                   "Введите логин и пароль ВКонтакте")
            return

        start_button.configure(state='disabled')
        progress.start()

        for idx, url in enumerate(urls_list):
            try:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                global RESULTS_FILE
                RESULTS_FILE = f'results_{timestamp}_{idx+1}.xlsx'
                process_images(url, vk_login, vk_password, show_completion=False)
            except Exception as e:
                logging.error(f"Ошибка при обработке ссылки {url}: {str(e)}")
                continue

        progress.stop()
        start_button.configure(state='normal')
        messagebox.showinfo("Завершено", f"Обработка всех {len(urls_list)} ссылок завершена")

    root.configure(bg="#1e1e2e")
    root.resizable(False, False)

    style = ttk.Style()
    style.theme_use('default')
    style.configure("TLabel",
                    font=("Segoe UI", 11),
                    background="#1a1b26",
                    foreground="#a9b1d6")
    style.configure("TEntry",
                    font=("Segoe UI", 11),
                    fieldbackground="#24283b",
                    foreground="#c0caf5",
                    insertcolor="#c0caf5")
    style.configure("TButton",
                    font=("Segoe UI", 11, "bold"),
                    padding=10,
                    background="#7aa2f7",
                    foreground="#ffffff")
    style.configure("Header.TLabel",
                    font=("Segoe UI", 24, "bold"),
                    foreground="#c0caf5",
                    background="#1a1b26")
    style.configure("Main.TFrame", background="#1a1b26")
    style.configure("Blue.Horizontal.TProgressbar",
                    background="#7aa2f7",
                    troughcolor="#24283b")
    style.configure("Header.TLabel",
                    font=("Montserrat", 28, "bold"),
                    foreground="#ffffff",
                    background="#1e1e2e")
    style.configure("Main.TFrame", background="#1e1e2e")
    style.configure("Blue.Horizontal.TProgressbar",
                    background="#7c3aed",
                    troughcolor="#2d2d3f")

    main_frame = ttk.Frame(root, padding=25, style="Main.TFrame")
    main_frame.pack(fill=tk.BOTH, expand=True)

    header = ttk.Label(main_frame, text="PhotoDNA", style="Header.TLabel")
    header.pack(pady=(0, 8))

    subheader = ttk.Label(main_frame,
                          text="Умный поиск и анализ изображений",
                          font=("Segoe UI", 12),
                          background="#1a1b26",
                          foreground="#7aa2f7")
    subheader.pack(pady=(0, 25))

    input_frame = ttk.Frame(main_frame, style="Main.TFrame")
    input_frame.pack(fill=tk.X, pady=10)

    label = ttk.Label(input_frame,
                      text="Введите ссылку на альбом или фотографию:",
                      font=("Segoe UI", 11))
    label.pack(pady=(0, 8))

    entry_style = ttk.Style()
    entry_style.configure("Custom.TEntry",
                          fieldbackground="#2d2d3f",
                          foreground="#ffffff",
                          insertcolor="#ffffff",
                          borderwidth=0)

    # Фрейм для логина/пароля
    auth_frame = ttk.Frame(input_frame, style="Main.TFrame")
    auth_frame.pack(pady=(0, 10))

    ttk.Label(auth_frame, text="Логин ВК:",
              font=("Segoe UI", 11)).pack(side=tk.LEFT, padx=5)
    login_entry = ttk.Entry(auth_frame,
                            width=30,
                            font=("Montserrat", 11),
                            style="Custom.TEntry")
    login_entry.pack(side=tk.LEFT, padx=5)

    ttk.Label(auth_frame, text="Пароль ВК:",
              font=("Segoe UI", 11)).pack(side=tk.LEFT, padx=5)
    password_entry = ttk.Entry(auth_frame,
                               width=30,
                               font=("Montserrat", 11),
                               style="Custom.TEntry",
                               show="*")
    password_entry.pack(side=tk.LEFT, padx=5)

    # Фрейм для ввода ссылок
    entry_frame = ttk.Frame(input_frame, style="Main.TFrame")
    entry_frame.pack(pady=(0, 5))

    entry = ttk.Entry(entry_frame,
                      width=80,
                      font=("Montserrat", 11),
                      style="Custom.TEntry")
    entry.pack(side=tk.LEFT, pady=(0, 5), ipady=8)

    add_button = ttk.Button(entry_frame, text="+", width=3, command=add_url)
    add_button.pack(side=tk.LEFT, padx=5)

    # Список ссылок
    urls_frame = ttk.Frame(input_frame, style="Main.TFrame")
    urls_frame.pack(fill=tk.X, pady=10)

    urls_listbox = tk.Listbox(urls_frame,
                              width=70,
                              height=6,
                              font=("Segoe UI", 11),
                              bg="#24283b",
                              fg="#c0caf5",
                              selectbackground="#7aa2f7",
                              selectforeground="#ffffff",
                              borderwidth=0)
    urls_listbox.pack(side=tk.LEFT, fill=tk.X, padx=(0, 10))

    scrollbar = ttk.Scrollbar(urls_frame,
                              orient=tk.VERTICAL,
                              command=urls_listbox.yview)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    urls_listbox.configure(yscrollcommand=scrollbar.set)

    remove_button = ttk.Button(urls_frame,
                               text="Удалить",
                               command=remove_url,
                               width=12)
    remove_button.pack(side=tk.RIGHT)

    def show_context_menu(event):
        context_menu.tk_popup(event.x_root, event.y_root)

    context_menu = tk.Menu(root, tearoff=0, bg="#2d2d3f", fg="#ffffff")
    context_menu.add_command(label="Вставить",
                             command=lambda: entry.event_generate("<<Paste>>"),
                             activebackground="#7c3aed",
                             activeforeground="#ffffff")
    context_menu.add_command(label="Копировать",
                             command=lambda: entry.event_generate("<<Copy>>"),
                             activebackground="#7c3aed",
                             activeforeground="#ffffff")
    entry.bind("<Button-3>", show_context_menu)

    progress_frame = ttk.Frame(main_frame, style="Main.TFrame")
    progress_frame.pack(fill=tk.X, pady=15)

    progress = ttk.Progressbar(progress_frame,
                               orient=tk.HORIZONTAL,
                               length=700,
                               mode='indeterminate',
                               style="Blue.Horizontal.TProgressbar")
    progress.pack()

    def on_start():
        if not urls_list:
            messagebox.showwarning(
                "PhotoDNA",
                "Пожалуйста, добавьте хотя бы одну ссылку на альбом или фотографию."
            )
            return

        vk_login = login_entry.get().strip()
        vk_password = password_entry.get().strip()

        if not vk_login or not vk_password:
            messagebox.showwarning("PhotoDNA",
                                   "Введите логин и пароль ВКонтакте")
            return

        start_button.configure(state='disabled')
        progress.start()

        for idx, url in enumerate(urls_list):
            try:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                global RESULTS_FILE
                RESULTS_FILE = f'results_{timestamp}_{idx+1}.xlsx'
                process_images(url, vk_login, vk_password, show_completion=False)
            except Exception as e:
                logging.error(f"Ошибка при обработке ссылки {url}: {str(e)}")
                continue

        progress.stop()
        start_button.configure(state='normal')
        messagebox.showinfo("Завершено", f"Обработка всех {len(urls_list)} ссылок завершена")

    def paste(event):
        try:
            entry.event_generate("<<Paste>>")
        except:
            pass

    entry.bind("<Control-v>", paste)
    entry.bind("<Command-v>", paste)

    start_button = ttk.Button(main_frame,
                              text="Начать обработку",
                              command=on_start)
    start_button.pack(pady=20)

    root.mainloop()
