import cv2
import numpy as np

class Processor:
    """
    Класс для загрузки и обработки изображений.
    Содержит методы для:
    - загрузки изображения (cv2.imread)
    - перевода в оттенки серого
    - бинаризации методом Оцу
    - морфологического закрытия
    - сохранения результата
    """

    def __init__(self):
        self._image = None      # исходное цветное изображение (BGR)
        self.gray = None        # серое изображение
        self.binary = None      # бинарное изображение после закрытия
        self.threshold = None   # вычисленный порог Оцу

    def load_image(self, file_path):
        """
        Загружает изображение с диска.
        Возвращает True при успехе, иначе False.
        """
        if not file_path:
            return False
        img = cv2.imread(file_path)
        if img is None:
            return False
        self._image = img
        self.gray = None
        self.binary = None
        self.threshold = None
        return True

    def process(self):
        """
        Выполняет полный конвейер обработки:
        1. Преобразование в оттенки серого.
        2. Бинаризация методом Оцу (cv2.THRESH_BINARY + cv2.THRESH_OTSU).
        3. Морфологическое закрытие (cv2.MORPH_CLOSE) с эллиптическим ядром 5x5.
        Возвращает кортеж (порог, бинарное изображение) или (None, None) при ошибке.
        """
        if self._image is None:
            return None, None

        # 1. Серый
        self.gray = cv2.cvtColor(self._image, cv2.COLOR_BGR2GRAY)

        # 2. Оцу
        ret, binary = cv2.threshold(self.gray, 0, 255,
                                    cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        self.threshold = ret

        # 3. Закрытие
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
        self.binary = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)

        return self.threshold, self.binary

    def save_result(self, save_path):
        """
        Сохраняет бинарное изображение в файл (рекомендуется PNG).
        Возвращает True при успехе.
        """
        if self.binary is None:
            return False
        return cv2.imwrite(save_path, self.binary)