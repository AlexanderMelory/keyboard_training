import glob  # Для доступа к файлам
import random  # Необходим для доступа к рандомному файлу
import sys
import time

from virtualKey import vkeys  # Словарь виртуальных ключей
from PyQt5 import QtWidgets, QtGui
from PyQt5.QtCore import QThread

from qt_designer import design


class TimerThread(QThread):
    """Отдельный поток, реализующий отслеживание времени"""

    def __init__(self, mainWindow, parent=None):
        super().__init__()
        self.mainWindow = mainWindow

    def run(self):
        worktime = 0
        amount_char = len(self.mainWindow.breaked_text)  # Количество символов в строке
        while True:
            time.sleep(1)
            worktime += 1
            self.mainWindow.label_Time.setText("Время:" + "\n" + str(worktime))
            if not self.mainWindow.isChronometrStarted:  # Подсчитываем скорость печати
                self.mainWindow.label_Speed.setText("Скорость:" +
                                                    "\n" + str("%.2f" %
                                                               float(amount_char / worktime)))
                break


class KbTrainingWindow(QtWidgets.QMainWindow, design.Ui_MainWindow):
    def __init__(self):
        # Доступ к дизайну kbTrainingWindow, методам и т д
        super().__init__()

        self.setupUi(self)  # Инициализация дизайна

        self.timer = TimerThread(mainWindow=self)

        self.textBank = []  # Банк текстов
        self.scan_textBank()  # Сканирование и пополнение банка текстов

        self.selected_text = []  # Список строк текста
        self.breaked_text = []  # Разбитая на символы строка текста оказывается здесь
        self.mistakes = 0  # Ошибки, в течение игровой сессии

        self.isTextSelected = False  # Выбран ли текстовый файл
        self.isRowSelected = False  # Выбрана ли строка в текстовом файле
        self.isChronometrStarted = False  # При вводе первого символа - запускает хронометр
        self.checkTextSelected()  # Выполняет проверку, выбран ли текст

    def scan_textBank(self):
        """Сканирует банк текстов перед стартом игры"""

        for text_file in glob.glob("text_for_game/*txt"):
            self.textBank.append(text_file)

        if not self.textBank:
            self.label_OutputText.setText("Банк текстов пуст, пополните его")

    def open_random_text(self):
        """Открывает рандомный текстовый файл"""

        if self.textBank and not self.isTextSelected:

            with open(random.choice(self.textBank), 'r', encoding="UTF-8") as f:
                selected_text = f.readlines()
                f.close()

            self.isTextSelected = True

            return selected_text  # Список строк текста

        else:
            self.label_OutputText.setText("Неудалось открыть текстовый файл")

    def select_row(self, selected_text):
        if self.isTextSelected and not self.isRowSelected:
            selected_row = selected_text[0]
            selected_row = selected_row.replace(",", "")  # Убираем ненужные запятые из текста
            selected_text.pop(0)

            self.isRowSelected = True

            return str(selected_row)

        elif not selected_text:
            self.isTextSelected = False  # Если строка не выбрана - значит текст кончился
            self.checkTextSelected()

    def break_text(self, selected_row):
        """Разбивает текст на символы"""

        if selected_row:
            selected_row = selected_row.strip()  # Убираем ненужные пробелы слева вначале, справа в конце
            break_text = list(selected_row)
            return break_text

        else:
            self.label_OutputText.setText("Не удалось разбить текст на символы")

    def set_outputText(self, selected_row):
        """Выводит выбранный текст в поле label вывода текста"""

        if selected_row:
            self.label_OutputText.setText(selected_row)

        else:
            self.label_OutputText.setText("Неудалось вывести строку из текста на экран")

    def keyPressEvent(self, event: QtGui.QKeyEvent):
        """Отслеживание нажатий клавиш и проверка корректности ввода"""

        if self.breaked_text and vkeys.get(event.nativeVirtualKey()):
            if self.breaked_text[0] == vkeys.get(event.nativeVirtualKey()):

                if self.label_InputText.text() == "Ввод текста":  # Убираем стартовый текст
                    self.label_InputText.setText("")
                    self.isChronometrStarted = True
                    self.timer.start()

                self.breaked_text.pop(0)
                self.label_InputText.setText(self.label_InputText.text() + str(vkeys.get(event.nativeVirtualKey())))

                if len(self.breaked_text) == 0:
                    self.isRowSelected = False
                    self.isChronometrStarted = False

                    if not self.selected_text:
                        self.isTextSelected = False
                    self.checkTextSelected()
            else:
                self.mistakes += 1
                self.label_Mistakes.setText("Ошибки:\n" + str(self.mistakes))

    def checkTextSelected(self):
        """Выполняет проверку, выбран ли текстовый файл"""

        if not self.isTextSelected:  # Открытие рандомного текстового файла
            self.selected_text = self.open_random_text()

        selected_row = self.select_row(self.selected_text).lower()
        self.label_InputText.setText("Ввод текста")
        self.breaked_text = self.break_text(selected_row)  # Разбиваем на буквы
        self.set_outputText(selected_row)


def main():
    app = QtWidgets.QApplication(sys.argv)
    window = KbTrainingWindow()
    window.show()
    app.exec_()


if __name__ == '__main__':
    main()
