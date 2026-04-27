import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QComboBox, QPushButton, QLabel, QMessageBox
)

from USB_8SMC5 import USB_8SMC5

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
        self.setWindowTitle("Rotation Selector")

        self.device_list = device_list
        # Поля для выбора
        #self.fields = ["X", "Y", "Z"]
        self.fields = []
        for d in device_list:
            self.fields.append(str(d.gser))

        # Комбобоксы и метки
        self.comboboxes = {}
        for name in ["Yaw", "Pitch", "Roll"]:
            cb = QComboBox()
            cb.addItem("")  # пустое значение по умолчанию
            cb.addItems(self.fields)
            cb.currentIndexChanged.connect(self.update_comboboxes)
            self.comboboxes[cb] = name

        # Словарь для хранения предыдущего выбора
        self.previous_selection = {cb: "" for cb in self.comboboxes}

        # Кнопки
        self.ok_btn = QPushButton("Ok")
        self.cancel_btn = QPushButton("Cancel")
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
            exclude_list.apend(d.port_name)
            device_list.append(d)
    except:
        pass
    window = RotationSelector(device_list)
    window.show()
    sys.exit(app.exec())