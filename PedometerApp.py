import serial
from PyQt5.QtGui import QPixmap

import New_graf  # Это наш конвертированный файл дизайна
from PyQt5 import QtWidgets
from PyQt5.QtCore import QThread
from PyQt5.QtWidgets import QFileDialog
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt
from scipy.ndimage.filters import gaussian_filter
import mplcursors
import numpy as np
import New_graf
import save_contour


# Поток для считывания серии наблюдений
class ReadingFlow(QThread):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window

    def run(self):
        while self.main_window.thread_run:
            self.main_window.read_data_plata()

class SaveContour(QtWidgets.QMainWindow,save_contour.Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.showMaximized()
        self.scene = QtWidgets.QGraphicsScene(self)
        pixmap = QPixmap("Ноги.png")
        self.label.setPixmap(pixmap)


class PedometerApp(QtWidgets.QMainWindow, New_graf.Ui_MainWindow):
    # Конфигуратор приложения
    def __init__(self, parent = None):
        super().__init__(parent)
        self.twoWindow = None
        self.setupUi(self)
        self.showMaximized()  # Приложение во весь экран
        # Создание глобальных переменных
        self.comports = serial_ports()  # Вызов функции определения COM - порта
        self.start_flow = ReadingFlow(main_window=self)  # Создание нового потока
        self.np_arr = []  # Для хранения серии наблюдений
        self.marks = []   # Для хранения массива из Arduino
        self.ArduinoSerial = False
        self.thread_run = False     # Для остановки считывания данных в потоке
        # Создание виджета для отрисовки графиков
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout(self.graf)
        self.horizontalLayout_4.setObjectName('horizontalLayout_4')
        self.figure = plt.figure()
        self.canvas = FigureCanvas(self.figure)
        self.horizontalLayout_4.addWidget(self.canvas)
        # Создание меню для подключения платы
        self.com_port = self.menu.addMenu("COM порт")
        self.submenu_com_port = []
        for i in self.comports:
            self.submenu_com_port = (self.com_port.addAction(i))
            self.submenu_com_port.triggered.connect(self.connection_plata)
        # Создание меню для скорости в bod подключения платы
        # Сигналы от элементов приложения
        self.record.clicked.connect(self.record_button)  # Считывание данных с платы
        self.save_png.clicked.connect(self.save_as_png)  # Сохранение графика как картинки
        # Кнопка закрыть изначально вот это "self.close_app.clicked.connect(app.quit)  # закрытие приложения"
        self.close_app.clicked.connect(self.open_new_windows)  # закрытие приложения
        self.open_data.clicked.connect(self.open_data_np)   # Открытие данных
        self.save_png_menu.triggered.connect(self.save_as_png)  # сохранение снимка
        self.open_read_menu.triggered.connect(self.open_data_np)
        self.ones_read.toggled.connect(self.mode_shot)
        self.series_read.toggled.connect(self.mode_shot)
        self.slider_shot.sliderMoved.connect(self.change_shot_slider)
        self.number_shot.valueChanged.connect(self.change_shot_spinbox)
        self.record.setStyleSheet('QPushButton {background-color: green;}')  # Установка фона кнопки
        self.record.setText('Запись')  # Текст кнопки

    def open_new_windows(self):
        self.twoWindow = SaveContour()
        self.twoWindow.show()

    # Изменение показаний SpiBox
    def change_shot_spinbox(self):
        if self.record.text() == 'Запись':
            self.slider_shot.setValue(self.number_shot.value())
            self.plot_in_app(self.np_arr[self.number_shot.value() - 1])

    # Изменение показаний Slider
    def change_shot_slider(self):
        self.number_shot.setValue(self.slider_shot.sliderPosition())
        self.plot_in_app(self.np_arr[self.slider_shot.sliderPosition() - 1])

    # Подключение к плате
    def connection_plata(self):
        speed = False
        for i in self.menu_2.actions():
            if not speed:
                speed = i.isChecked()
            if speed:
                speed = i.text()
                break
        print(speed)
        if not self.ArduinoSerial:
            self.ArduinoSerial = serial.Serial(self.comports[0], speed)  # Установка параметров платы
            self.thread_run = False

    # Отрисовка графиков. Функция принимает массив
    def plot_in_app(self, array):
        self.figure.clear()
        #array = 0.1806*array**2 - 245.3*array + 8.327e+04
        max_array = np.amax(array)
        print(sum(sum(array)))
        #array = gaussian_filter(array, sigma=(0.7, 0.7), mode='reflect')
        plt.imshow(array, extent=([0, len(array), 0, len(array)]), cmap='Greens',
                   interpolation='none', vmin=0, vmax=max_array)
        if self.legend.isChecked():
            plt.colorbar(label="Давление кг/см^2")
        if not self.axis.isChecked():
            plt.axis([0, len(array), 0, len(array)])
            plt.xticks(range(0, len(array)))
            plt.yticks(range(0, len(array)))
            plt.tick_params(colors='w', which='both')
        if self.grid.isChecked():
            plt.grid(color='black', linestyle='-', linewidth=2)
        if self.cursor_mouse.isChecked():
            cursor = mplcursors.cursor(hover=False)

            @cursor.connect("add")
            def on_add(sel):
                i, j = sel.target.index
                sel.annotation.set_text(str(array[i][j]) + ' kg')
        self.canvas.draw()

    # Переделать открытие файлов
    # Открытие сохраненных массивов numpy
    def open_data_np(self):
        file, check = QFileDialog.getOpenFileName(None, "QFileDialog.getOpenFileName()", "", "Data (*.NPY)")
        if file == '':
            return
        self.np_arr = np.load(file)
        self.number_shot.setMaximum(len(self.np_arr))
        self.number_shot.setValue(len(self.np_arr))
        self.slider_shot.setMaximum(len(self.np_arr))
        self.slider_shot.setValue(len(self.np_arr))
        self.plot_in_app(self.np_arr[-1])

    # Режим чтения данных серия/снимок
    def mode_shot(self):
        if self.ones_read.isChecked():
            self.record.setStyleSheet('QPushButton {background-color: green;}')  # Установка фона кнопки
            self.record.setText('Снимок')  # Текст кнопки
            return
        self.record.setStyleSheet('QPushButton {background-color: green;}')  # Установка фона кнопки
        self.record.setText('Запись')  # Текст кнопки

    # Запуск потока записи
    def record_button(self):
        if not self.ArduinoSerial:
            return
        if self.record.text() == 'Стоп':
            self.record.setStyleSheet('QPushButton {background-color: Green;}')
            self.record.setText('Запись')
            self.thread_run = False
            return
        if self.series_read.isChecked() and not self.thread_run:
            self.np_arr = []
            self.thread_run = True
            self.start_flow.start()
            self.record.setStyleSheet('QPushButton {background-color: red;}')
            self.record.setText('Стоп')
        if self.record.text() == 'Снимок':
            self.np_arr = []
            self.read_data_plata()

    # Считывание данных с платы из приложения
    def read_data_plata(self):
        self.marks = []
        self.marks = self.get_serial_data()
        self.np_arr.append(self.marks)
        self.plot_in_app(self.marks)
        self.number_shot.setMaximum(len(self.np_arr))
        self.number_shot.setValue(len(self.np_arr))
        self.slider_shot.setMaximum(len(self.np_arr))
        self.slider_shot.setValue(len(self.np_arr))

    # Сохранение графика в виде картинки
    def save_as_png(self):
        # доделать сохранение конкретной картинки np_arr + сохранение модели стл
        file, check = QFileDialog.getSaveFileName(None, "QFileDialog getSaveFileName() Demo", "", "картинка (*.png)")
        if file == '':
            return
        plt.savefig(file)
        file = file.rsplit('.', maxsplit=1)
        file = file[0].rsplit('/', maxsplit=1)
        self.np_arr = np.array(self.np_arr, dtype=float)
        np.save(file[-1], self.np_arr)
        self.np_arr = []

    # Считывание данных с ArduinoSerial функция
    def get_serial_data(self):
        self.ArduinoSerial.write('1'.encode())  # передаем
        massive = []
        for i in range(1024):
            data = self.ArduinoSerial.readline()
            data = data.decode('UTF-8')
            massive.append(int(data))
        massive = np.array(massive)
        massive = np.reshape(massive, (-1, 32))
        return massive


def serial_ports():
    if sys.platform.startswith('win'):
        ports = ['COM%s' % (i + 1) for i in range(20)]
    else:
        raise EnvironmentError('Unsupported platform')
    result = []
    for port in ports:
        try:
            s = serial.Serial(port)
            s.close()
            result.append(port)
        except (OSError, serial.SerialException):
            pass
    return result


# Если мы запускаем файл напрямую, а не импортируем
if __name__ == '__main__':
    import sys
    app = QtWidgets.QApplication(sys.argv)  # Новый экземпляр QApplication
    window = PedometerApp()  # Создаём объект класса ExampleApp
    window.show()  # Показываем окно
    sys.exit(app.exec_())  # и запускаем приложение
