import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image
import shutil


class FileConverterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Универсальный конвертер файлов")
        self.root.geometry("600x400")

        # Поддерживаемые форматы (перенесено в начало)
        self.supported_image_formats = {
            'JPEG': ['jpg', 'jpeg'],
            'PNG': ['png'],
            'BMP': ['bmp'],
            'GIF': ['gif'],
            'TIFF': ['tif', 'tiff'],
            'WEBP': ['webp']
        }

        self.supported_text_formats = {
            'TXT': ['txt'],
            'CSV': ['csv'],
            'JSON': ['json'],
            'XML': ['xml'],
            'HTML': ['html', 'htm'],
            'MD': ['md']
        }

        # Переменные
        self.input_files = []
        self.output_format = tk.StringVar()
        self.output_folder = tk.StringVar()
        self.conversion_mode = tk.StringVar(value="copy")

        # Создание интерфейса
        self.create_widgets()

    def create_widgets(self):
        # Фрейм для выбора файлов
        file_frame = ttk.LabelFrame(self.root, text="Выберите файлы для конвертации", padding=10)
        file_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Кнопка выбора файлов
        ttk.Button(file_frame, text="Выбрать файлы", command=self.select_files).pack(pady=5)

        # Список выбранных файлов
        self.file_listbox = tk.Listbox(file_frame, height=8, selectmode=tk.EXTENDED)
        self.file_listbox.pack(fill=tk.BOTH, expand=True, pady=5)

        # Кнопка очистки списка
        ttk.Button(file_frame, text="Очистить список", command=self.clear_files).pack(pady=5)

        # Фрейм для настроек конвертации
        settings_frame = ttk.LabelFrame(self.root, text="Настройки конвертации", padding=10)
        settings_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Выбор формата назначения
        ttk.Label(settings_frame, text="Целевой формат:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=2)
        self.format_combobox = ttk.Combobox(settings_frame, textvariable=self.output_format, state="readonly")
        self.format_combobox.grid(row=0, column=1, sticky=tk.EW, padx=5, pady=2)

        # Выбор папки назначения
        ttk.Label(settings_frame, text="Папка для сохранения:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=2)
        ttk.Entry(settings_frame, textvariable=self.output_folder).grid(row=1, column=1, sticky=tk.EW, padx=5, pady=2)
        ttk.Button(settings_frame, text="Обзор", command=self.select_output_folder).grid(row=1, column=2, padx=5,
                                                                                         pady=2)

        # Режим конвертации
        ttk.Label(settings_frame, text="Режим конвертации:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=2)
        ttk.Radiobutton(settings_frame, text="Копировать структуру папок", variable=self.conversion_mode,
                        value="copy").grid(row=2, column=1, sticky=tk.W, padx=5, pady=2)
        ttk.Radiobutton(settings_frame, text="Сохранять в одной папке", variable=self.conversion_mode,
                        value="flat").grid(row=3, column=1, sticky=tk.W, padx=5, pady=2)

        # Кнопка конвертации
        ttk.Button(self.root, text="Конвертировать", command=self.convert_files).pack(pady=10)

        # Обновляем доступные форматы
        self.update_available_formats()

    def update_available_formats(self):
        # Собираем все доступные форматы
        all_formats = []

        # Добавляем изображения
        for fmt, exts in self.supported_image_formats.items():
            all_formats.append(f"{fmt} ({', '.join(exts)})")

        # Добавляем текстовые форматы
        for fmt, exts in self.supported_text_formats.items():
            all_formats.append(f"{fmt} ({', '.join(exts)})")

        # Добавляем просто копирование
        all_formats.append("Копировать как есть (изменить расширение)")

        self.format_combobox['values'] = all_formats
        if all_formats:
            self.format_combobox.current(0)

    def select_files(self):
        files = filedialog.askopenfilenames(
            title="Выберите файлы для конвертации",
            filetypes=[("Все файлы", "*.*")]
        )

        if files:
            self.input_files = list(files)
            self.file_listbox.delete(0, tk.END)
            for file in self.input_files:
                self.file_listbox.insert(tk.END, file)

    def clear_files(self):
        self.input_files = []
        self.file_listbox.delete(0, tk.END)

    def select_output_folder(self):
        folder = filedialog.askdirectory(title="Выберите папку для сохранения")
        if folder:
            self.output_folder.set(folder)

    def get_format_from_combobox(self):
        selected = self.output_format.get()
        if not selected:
            return None

        # Извлекаем формат из строки (например "JPEG (jpg, jpeg)" -> "jpeg")
        if "(" in selected:
            format_name = selected.split("(")[0].strip().lower()
            return format_name
        else:
            return None

    def convert_files(self):
        if not self.input_files:
            messagebox.showwarning("Ошибка", "Не выбраны файлы для конвертации")
            return

        output_folder = self.output_folder.get()
        if not output_folder:
            output_folder = os.path.dirname(self.input_files[0])
            self.output_folder.set(output_folder)

        selected_format = self.get_format_from_combobox()
        is_copy_only = "Копировать" in self.output_format.get()

        total_files = len(self.input_files)
        success_count = 0

        # Создаем прогресс-бар
        progress = tk.Toplevel(self.root)
        progress.title("Конвертация файлов")
        progress.geometry("400x100")

        progress_label = ttk.Label(progress, text="Конвертация файлов...")
        progress_label.pack(pady=5)

        progress_bar = ttk.Progressbar(progress, orient=tk.HORIZONTAL, length=300, mode='determinate')
        progress_bar.pack(pady=5)
        progress_bar['maximum'] = total_files

        self.root.update()

        for i, input_file in enumerate(self.input_files):
            try:
                filename = os.path.basename(input_file)
                name, ext = os.path.splitext(filename)
                ext = ext.lower()[1:] if ext else ""

                # Определяем папку назначения
                if self.conversion_mode.get() == "copy":
                    # Сохраняем структуру папок
                    rel_path = os.path.relpath(input_file, start=os.path.dirname(os.path.dirname(input_file)))
                    output_path = os.path.join(output_folder, os.path.dirname(rel_path))
                else:
                    # Все файлы в одну папку
                    output_path = output_folder

                os.makedirs(output_path, exist_ok=True)

                if is_copy_only:
                    # Просто копируем с новым расширением
                    if selected_format:
                        new_ext = selected_format
                    else:
                        new_ext = ext

                    output_file = os.path.join(output_path, f"{name}.{new_ext}")
                    shutil.copy2(input_file, output_file)
                    success_count += 1
                else:
                    # Определяем тип файла
                    is_image = any(ext in exts for exts in self.supported_image_formats.values())
                    is_text = any(ext in exts for exts in self.supported_text_formats.values())

                    if is_image and selected_format and selected_format.upper() in self.supported_image_formats:
                        # Конвертируем изображение
                        output_ext = self.supported_image_formats[selected_format.upper()][0]
                        output_file = os.path.join(output_path, f"{name}.{output_ext}")

                        try:
                            img = Image.open(input_file)
                            if img.mode == 'RGBA' and selected_format.upper() == 'JPEG':
                                img = img.convert('RGB')
                            img.save(output_file, format=selected_format.upper())
                            success_count += 1
                        except Exception as e:
                            messagebox.showwarning("Ошибка", f"Ошибка при конвертации {filename}: {str(e)}")
                            continue

                    elif is_text and selected_format and selected_format.upper() in [f.upper() for f in
                                                                                     self.supported_text_formats]:
                        # Для текстовых файлов просто копируем с новым расширением
                        output_ext = self.supported_text_formats[selected_format.upper()][0]
                        output_file = os.path.join(output_path, f"{name}.{output_ext}")
                        shutil.copy2(input_file, output_file)
                        success_count += 1
                    else:
                        # Неподдерживаемый формат - просто копируем
                        output_file = os.path.join(output_path, filename)
                        shutil.copy2(input_file, output_file)
                        success_count += 1

                progress_bar['value'] = i + 1
                progress_label.config(text=f"Обработано {i + 1} из {total_files} файлов")
                progress.update()

            except Exception as e:
                messagebox.showwarning("Ошибка", f"Ошибка при обработке файла {filename}: {str(e)}")
                continue

        progress.destroy()
        messagebox.showinfo("Готово",
                            f"Конвертация завершена. Успешно обработано {success_count} из {total_files} файлов.")


if __name__ == "__main__":
    root = tk.Tk()
    app = FileConverterApp(root)

    # Центрирование окна
    window_width = root.winfo_reqwidth()
    window_height = root.winfo_reqheight()
    position_right = int(root.winfo_screenwidth() / 2 - window_width / 2)
    position_down = int(root.winfo_screenheight() / 2 - window_height / 2)
    root.geometry(f"+{position_right}+{position_down}")

    root.mainloop()