import sys
from PyQt6.QtCore import Qt, QRectF, QSize
from PyQt6.QtGui import QPainter, QColor, QBrush, QPen, QFont
from PyQt6.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QComboBox,
    QPushButton,
    QLabel,
    QFrame,
    QAbstractButton,
)

from USB_8SMC5 import USB_8SMC5

#entities = ["Yaw", "Pitch", "Roll"]
entities = ["Азимут", "Угол Места", "Диафрагма"]


class ToggleSwitch(QAbstractButton):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setCheckable(True)
        self.setChecked(True)

        self.setCursor(Qt.CursorShape.PointingHandCursor)

        self._width = 40
        self._height = 15

    def sizeHint(self):
        return QSize(self._width, self._height)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, False)

        # ---------- Background ----------
        if self.isChecked():
            bg_color = QColor("#4d9aff")
        else:
            bg_color = QColor("#999999")

        painter.setBrush(QBrush(bg_color))
        painter.setPen(Qt.PenStyle.NoPen)

        # Прямоугольный фон
        painter.drawRect(0, 0, self._width, self._height)

        # ---------- Handle ----------
        handle_width = self._width // 2

        if self.isChecked():
            x = self._width - handle_width
        else:
            x = 0

        painter.setBrush(QBrush(QColor("white")))

        # Прямоугольный бегунок
        painter.drawRect(
            x,
            0,
            handle_width,
            self._height
        )

        painter.end()


class SectionWidget(QWidget):
    def __init__(self, title):
        super().__init__()

        main_layout = QVBoxLayout(self)

        # ---------- Header ----------
        header_layout = QHBoxLayout()

        title_label = QLabel(title)

        font = QFont()
        font.setBold(True)
        font.setPointSize(11)

        title_label.setFont(font)

        self.toggle = ToggleSwitch()

        header_layout.addWidget(title_label)
        header_layout.addStretch()
        header_layout.addWidget(self.toggle)

        # ---------- Content ----------
        self.content_widget = QWidget()

        content_layout = QVBoxLayout(self.content_widget)

        # Заглушки UI
        content_layout.addWidget(QLabel(f"{title}: UI component 1"))
        content_layout.addWidget(QPushButton("Button"))

        combo = QComboBox()
        combo.addItems(["Item 1", "Item 2", "Item 3"])

        content_layout.addWidget(combo)
        content_layout.addStretch()

        # ---------- Connections ----------
        self.toggle.toggled.connect(self.content_widget.setEnabled)

        # ---------- Main ----------
        main_layout.addLayout(header_layout)
        main_layout.addWidget(self.content_widget)


class MainApplicationWindow(QWidget):
    def __init__(self, rotations):
        super().__init__()
        self.setWindowTitle("Основное приложение")
        self.resize(800, 600)

        # Сохраняем выбранные значения
        self.rotations = rotations

        # Пока окно пустое, но можно вывести выбранные значения для проверки
        layout = QVBoxLayout()
        info_label = QLabel(f"Выбранные значения: {self.rotations}")
        layout.addWidget(info_label)
        self.setLayout(layout)


class RotationSelector(QWidget):
    def __init__(self, device_list):
        super().__init__()
        self.setWindowTitle("Назначение двигателей")

        self.device_list = device_list
        # Поля для выбора
        #self.fields = ["X", "Y", "Z"]
        self.fields = []
        for d in device_list:
            self.fields.append(str(d.gser()))

        # Комбобоксы и метки
        self.comboboxes = {}
        for name in entities:
            cb = QComboBox()
            cb.addItem("")  # пустое значение по умолчанию
            cb.addItems(self.fields)
            cb.currentIndexChanged.connect(self.update_comboboxes)
            self.comboboxes[cb] = name

        # Словарь для хранения предыдущего выбора
        self.previous_selection = {cb: "" for cb in self.comboboxes}

        # Кнопки
        self.ok_btn = QPushButton("Применить")
        self.cancel_btn = QPushButton("Закрыть")
        self.ok_btn.clicked.connect(self.ok_clicked)
        self.cancel_btn.clicked.connect(self.close)

        self.ok_btn.setEnabled(False)  # изначально выключена

        # Раскладка
        main_layout = QVBoxLayout()
        for cb, label_text in self.comboboxes.items():
            row = QHBoxLayout()
            row.addWidget(QLabel(label_text))
            row.addWidget(cb)
            main_layout.addLayout(row)

        btn_layout = QHBoxLayout()
        btn_layout.addWidget(self.ok_btn)
        btn_layout.addWidget(self.cancel_btn)
        main_layout.addLayout(btn_layout)

        self.setLayout(main_layout)

    def update_comboboxes(self):
        selected = set(cb.currentText() for cb in self.comboboxes if cb.currentText() != "")

        for cb in self.comboboxes:
            current = cb.currentText()
            cb.blockSignals(True)
            cb.clear()
            available = [""] + [f for f in self.fields if f not in selected or f == current]
            cb.addItems(available)
            cb.setCurrentText(current)
            cb.blockSignals(False)
            self.previous_selection[cb] = current
        
        # Проверяем: выбран ли хотя бы один комбобокс
        any_selected = any(cb.currentText() != "" for cb in self.comboboxes)
        self.ok_btn.setEnabled(any_selected)

    def ok_clicked(self):
        # Собираем выбранные значения
        rotations = {name: cb.currentText() for cb, name in self.comboboxes.items()}

        # Открываем окно основного приложения с передачей значений
        self.main_window = MainApplicationWindow(rotations)
        self.main_window.show()
        self.close()  # закрываем окно выбора


if __name__ == "__main__":
    app = QApplication(sys.argv)
    device_list = []
    exclude_list = []
    try:
        while True:
            d = USB_8SMC5(exclude_list)
            if d.port_name is None:
                break
            exclude_list.append(d.port_name)
            device_list.append(d)
    except Exception as e:
        print(f"Listing COM ports failed with error: {e}")
        pass
    window = RotationSelector(device_list)
    window.show()
    sys.exit(app.exec())