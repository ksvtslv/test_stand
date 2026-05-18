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


# =========================================================
# Toggle Switch
# =========================================================
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


# =========================================================
# Section Widget
# =========================================================
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


# =========================================================
# Main Window
# =========================================================
class MainApplicationWindow(QWidget):
    def __init__(self, rotations):
        super().__init__()

        self.rotations = rotations

        self.setWindowTitle("Основное приложение")
        self.resize(800, 600)

        main_layout = QHBoxLayout(self)

        # ===== Sections =====
        yaw_section = SectionWidget("Yaw")
        pitch_section = SectionWidget("Pitch")
        roll_section = SectionWidget("Roll")

        # ===== Separators =====
        separator1 = QFrame()
        separator1.setFrameShape(QFrame.Shape.VLine)
        separator1.setFrameShadow(QFrame.Shadow.Sunken)

        separator2 = QFrame()
        separator2.setFrameShape(QFrame.Shape.VLine)
        separator2.setFrameShadow(QFrame.Shadow.Sunken)

        # ===== Layout =====
        main_layout.addWidget(yaw_section)
        main_layout.addWidget(separator1)
        main_layout.addWidget(pitch_section)
        main_layout.addWidget(separator2)
        main_layout.addWidget(roll_section)

        main_layout.setStretch(0, 1)
        main_layout.setStretch(2, 1)
        main_layout.setStretch(4, 1)


# =========================================================
# Rotation Selector
# =========================================================
class RotationSelector(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Rotation Selector")

        self.fields = ["X", "Y", "Z"]

        self.comboboxes = {}

        for name in ["Yaw", "Pitch", "Roll"]:
            cb = QComboBox()

            cb.addItem("")
            cb.addItems(self.fields)

            cb.currentIndexChanged.connect(self.update_comboboxes)

            self.comboboxes[cb] = name

        self.ok_btn = QPushButton("Ok")
        self.cancel_btn = QPushButton("Cancel")

        self.ok_btn.setEnabled(False)

        self.ok_btn.clicked.connect(self.ok_clicked)
        self.cancel_btn.clicked.connect(self.close)

        # ---------- Layout ----------
        main_layout = QVBoxLayout(self)

        for cb, label_text in self.comboboxes.items():
            row = QHBoxLayout()

            row.addWidget(QLabel(label_text))
            row.addWidget(cb)

            main_layout.addLayout(row)

        btn_layout = QHBoxLayout()

        btn_layout.addWidget(self.ok_btn)
        btn_layout.addWidget(self.cancel_btn)

        main_layout.addLayout(btn_layout)

    def update_comboboxes(self):
        selected = set(
            cb.currentText()
            for cb in self.comboboxes
            if cb.currentText() != ""
        )

        for cb in self.comboboxes:
            current = cb.currentText()

            cb.blockSignals(True)

            cb.clear()

            available = [""] + [
                f for f in self.fields
                if f not in selected or f == current
            ]

            cb.addItems(available)
            cb.setCurrentText(current)

            cb.blockSignals(False)

        # Активировать OK если выбран хотя бы один
        any_selected = any(
            cb.currentText() != ""
            for cb in self.comboboxes
        )

        self.ok_btn.setEnabled(any_selected)

    def ok_clicked(self):
        rotations = {
            name: cb.currentText()
            for cb, name in self.comboboxes.items()
        }

        self.main_window = MainApplicationWindow(rotations)
        self.main_window.show()

        self.close()


# =========================================================
# Main
# =========================================================
if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = RotationSelector()
    window.resize(300, 150)
    window.show()

    sys.exit(app.exec())