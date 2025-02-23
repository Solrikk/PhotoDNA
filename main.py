     'Дата публикации', 'Текст поста', 'Переслано от',
                    'Заголовок', 'IP адрес'
            ]:
                if col not in df.columns:
                    df[col] = ''
            excel_file = RESULTS_FILE
            with pd.ExcelWriter(excel_file, engine='openpyxl') as writer:
                df.to_excel(writer, index=False, sheet_name='Результаты')
                workbook = writer.book
                worksheet = writer.sheets['Результаты']
                header_font = Font(bold=True, color="FFFFFF")
                header_fill = PatternFill(start_color="4F81BD",
                                          end_color="4F81BD",
                                          fill_type="solid")
                thin_border = Border(left=Side(style='thin'),
                                     right=Side(style='thin'),
                                     top=Side(style='thin'),
                                     bottom=Side(style='thin'))
                alignment_wrap = Alignment(wrap_text=True)
                for col in range(1, len(df.columns) + 1):
                    cell = worksheet.cell(row=1, column=col)
                    cell.font = header_font
                    cell.fill = header_fill
                    cell.border = thin_border
                    column_letter = get_column_letter(col)
                    max_length = max(
                        df.iloc[:, col - 1].astype(str).map(len).max(),
                        len(str(cell.value)))
                    adjusted_width = min(max_length + 2, 50)
                    worksheet.column_dimensions[
                        column_letter].width = adjusted_width
                    for row in range(2, len(df) + 2):
                        cell = worksheet.cell(row=row, column=col)
                        cell.alignment = alignment_wrap
                        if df.columns[col - 1] in [
                                'URL сайта', 'URL исходного фото',
                                'URL найденного фото'
                        ]:
                            url = cell.value
                            if pd.notna(url) and url:
                                cell.value = "Ссылка"
                                cell.hyperlink = url
                                cell.style = "Hyperlink"
                if 'Схожесть' in df.columns:
                    similarity_col = df.columns.get_loc('Схожесть') + 1
                    for row in range(2, len(df) + 2):
                        similarity_value = df.iloc[row - 2]['Схожесть']
                        try:
                            similarity_percent = float(similarity_value)
                        except:
                            similarity_percent = 0.0
                        if similarity_percent >= SIMILARITY_THRESHOLD:
                            color_intensity = min(
                                int((similarity_percent - SIMILARITY_THRESHOLD)
                                    / (1.0 - SIMILARITY_THRESHOLD) * 255), 255)
                            fill_color = f"{255:02X}{255 - color_intensity:02X}{255 - color_intensity:02X}"
                            cell = worksheet.cell(row=row,
                                                  column=similarity_col)
                            cell.fill = PatternFill(start_color=fill_color,
                                                    end_color=fill_color,
                                                    fill_type="solid")
                        cell = worksheet.cell(row=row, column=similarity_col)
                        cell.border = thin_border
                for row in range(2, len(df) + 2):
                    for col in range(1, len(df.columns) + 1):
                        cell = worksheet.cell(row=row, column=col)
                        cell.border = thin_border
            logging.info(f"Данные успешно записаны в {excel_file}")
            messagebox.showinfo("Завершено",
                                f"Данные успешно записаны в {excel_file}")
        else:
            logging.info("Нет данных для записи.")
            messagebox.showinfo("Завершено", "Нет данных для записи.")
    except Exception as e:
        logging.error(f"Фатальная ошибка: {str(e)}")
        messagebox.showerror("Ошибка", f"Произошла ошибка: {str(e)}")
    finally:
        driver.quit()
        logging.info("Браузер закрыт")


def start_processing(album_url):
    if not album_url:
        messagebox.showwarning(
            "Внимание",
            "Пожалуйста, введите ссылку на альбом или фотографию ВКонтакте.")
        return

    if not (album_url.startswith('https://vk.com/album') or album_url.startswith('https://vk.com/photo')):
        messagebox.showwarning(
            "Ошибка",
            "Неверный формат ссылки. Используйте ссылку на альбом или фотографию ВКонтакте.")
        return

    try:
        process_images(album_url)
    except Exception as e:
        logging.error(f"Критическая ошибка при обработке: {str(e)}")
        messagebox.showerror("Ошибка", "Произошла ошибка при обработке изображений")
        cleanup_temp_files()


def create_gui():
    root = tk.Tk()
    root.title("PhotoDNA - Анализ схожих изображений")
    root.geometry("1000x600")
    root.configure(bg="#1e1e2e")
    root.resizable(False, False)

    style = ttk.Style()
    style.theme_use('default')
    style.configure("TLabel", 
                   font=("Montserrat", 12), 
                   background="#1e1e2e",
                   foreground="#ffffff")
    style.configure("TEntry", 
                   font=("Montserrat", 11),
                   fieldbackground="#2d2d3f",
                   foreground="#ffffff",
                   insertcolor="#ffffff")
    style.configure("TButton",
                   font=("Montserrat", 11, "bold"),
                   padding=12,
                   background="#7c3aed",
                   foreground="#ffffff")
    style.configure("Header.TLabel",
                   font=("Montserrat", 28, "bold"),
                   foreground="#ffffff",
                   background="#1e1e2e")
    style.configure("Main.TFrame", 
                   background="#1e1e2e")
    style.configure("Blue.Horizontal.TProgressbar",
                   background="#7c3aed",
                   troughcolor="#2d2d3f")

    main_frame = ttk.Frame(root, padding=30, style="Main.TFrame")
    main_frame.pack(fill=tk.BOTH, expand=True)

    header = ttk.Label(main_frame, text="PhotoDNA", style="Header.TLabel")
    header.pack(pady=(0, 5))

    subheader = ttk.Label(main_frame,
                          text="Умный поиск и анализ изображений",
                          font=("Segoe UI", 12),
                          background="#f0f2f5",
                          foreground="#666666")
    subheader.pack(pady=(0, 20))

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

    entry_frame = ttk.Frame(input_frame, style="Main.TFrame")
    entry_frame.pack(pady=(0, 5))

    entry = ttk.Entry(entry_frame, 
                     width=80, 
                     font=("Montserrat", 11),
                     style="Custom.TEntry")
    entry.pack(pady=(0, 5), ipady=8)

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
        album_url = entry.get().strip()
        if album_url:
            start_button.configure(state='disabled')
            progress.start()
            root.update_idletasks()
            start_processing(album_url)
            progress.stop()
            start_button.configure(state='normal')
        else:
            messagebox.showwarning(
                "PhotoDNA",
                "Пожалуйста, введите ссылку на альбом или фотографию.")

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


if __name__ == "__main__":
    create_gui()
def cleanup_temp_files():
    try:
        import glob
        for temp_file in glob.glob("temp_image_*.jpg"):
            try:
                os.remove(temp_file)
                logging.info(f"Удален временный файл: {temp_file}")
            except:
                pass
    except Exception as e:
        logging.error(f"Ошибка при очистке временных файлов: {str(e)}")