import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
import cv2
from processor import Processor

class App(tk.Tk):
    """
    Главное окно с двумя вкладками (ttk.Notebook):
    - Оригинал: загрузка, запуск сегментации, отображение порога.
    - Результат: показ бинарной маски, кнопка сохранения.
    """

    def __init__(self):
        super().__init__()
        self.title("Бинаризация Оцу + Морфологическое закрытие дыр")
        self.geometry("700x600")

        self.processor = Processor()
        self.photo_orig = None    # для хранения PhotoImage
        self.photo_result = None

        # Создание вкладок
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(expand=True, fill="both")

        # Вкладка "Оригинал"
        self.tab_orig = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_orig, text="Оригинал")
        self._init_tab_orig()

        # Вкладка "Результат"
        self.tab_res = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_res, text="Результат")
        self._init_tab_res()

    def _init_tab_orig(self):
        """Настройка виджетов на вкладке «Оригинал»."""
        # Панель управления
        ctrl = ttk.Frame(self.tab_orig)
        ctrl.pack(fill="x", padx=10, pady=10)

        btn_load = ttk.Button(ctrl, text="Загрузить изображение",
                              command=self._load_image)
        btn_load.pack(side="left", padx=5)

        btn_seg = ttk.Button(ctrl, text="Запустить сегментацию",
                             command=self._run_segmentation)
        btn_seg.pack(side="left", padx=5)

        self.lbl_thr = ttk.Label(ctrl, text="Порог: не вычислен")
        self.lbl_thr.pack(side="left", padx=20)

        # Область предпросмотра
        self.lbl_orig_img = ttk.Label(self.tab_orig, text="Изображение не загружено")
        self.lbl_orig_img.pack(expand=True)

    def _init_tab_res(self):
        """Настройка виджетов на вкладке «Результат»."""
        ctrl = ttk.Frame(self.tab_res)
        ctrl.pack(fill="x", padx=10, pady=10)

        self.btn_save = ttk.Button(ctrl, text="Сохранить результат",
                                   command=self._save_result, state="disabled")
        self.btn_save.pack(side="left", padx=5)

        self.lbl_res_img = ttk.Label(self.tab_res, text="Результат пока отсутствует")
        self.lbl_res_img.pack(expand=True)

    def _load_image(self):
        """Обработчик кнопки «Загрузить изображение»."""
        path = filedialog.askopenfilename(
            filetypes=[("Изображения", "*.jpg *.jpeg *.png *.bmp *.tiff")]
        )
        if not path:
            return

        if not self.processor.load_image(path):
            messagebox.showerror("Ошибка", "Не удалось загрузить изображение")
            return

        # Отображение загруженного изображения
        try:
            img = Image.open(path)
            img.thumbnail((550, 400))
            self.photo_orig = ImageTk.PhotoImage(img)
            self.lbl_orig_img.config(image=self.photo_orig, text="")
            self.lbl_thr.config(text="Порог: не вычислен")
            # Сброс результата
            self.lbl_res_img.config(image="", text="Результат пока отсутствует")
            self.btn_save.config(state="disabled")
            self.photo_result = None
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось отобразить изображение:\n{e}")

    def _run_segmentation(self):
        """Обработчик кнопки «Запустить сегментацию»."""
        if self.processor._image is None:
            messagebox.showwarning("Предупреждение", "Сначала загрузите изображение")
            return

        thr, binary = self.processor.process()
        if binary is None:
            messagebox.showerror("Ошибка", "Не удалось выполнить сегментацию")
            return

        self.lbl_thr.config(text=f"Порог: {thr:.0f}")

        # Отображение бинарного изображения
        try:
            # Для отображения в Tkinter нужно преобразовать в RGB
            display = cv2.cvtColor(binary, cv2.COLOR_GRAY2RGB)
            pil_img = Image.fromarray(display)
            pil_img.thumbnail((550, 400))
            self.photo_result = ImageTk.PhotoImage(pil_img)
            self.lbl_res_img.config(image=self.photo_result, text="")
            self.btn_save.config(state="normal")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка отображения результата:\n{e}")

    def _save_result(self):
        """Обработчик кнопки «Сохранить результат»."""
        if self.processor.binary is None:
            messagebox.showwarning("Предупреждение", "Сначала выполните сегментацию")
            return
        path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG", "*.png"), ("JPEG", "*.jpg")]
        )
        if not path:
            return
        if self.processor.save_result(path):
            messagebox.showinfo("Успех", f"Результат сохранён в {path}")
        else:
            messagebox.showerror("Ошибка", "Не удалось сохранить файл")

if __name__ == "__main__":
    app = App()
    app.mainloop()