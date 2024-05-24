from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QPushButton
from PyQt6.QtGui import QFont, QPixmap
from PyQt6.QtCore import Qt
import sys


class KPIData:
    def __init__(self, value, unit, icon_path):
        self.value = value
        self.unit = unit
        self.icon_path = icon_path


class KPICard(QFrame):
    def __init__(self, kpi_data: KPIData):
        super().__init__()

        self.setFrameShape(QFrame.Shape.NoFrame)
        self.setLineWidth(0)
        self.setStyleSheet("background-color: white; border-radius: 10px;")

        self.main_layout = QVBoxLayout()
        self.value_layout = QHBoxLayout()

        self.value_label = QLabel("{:,}".format(kpi_data.value))
        self.value_label.setFont(QFont('Arial', 24, QFont.Weight.Bold))
        self.value_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)

        self.icon_label = QLabel()
        self.icon_pixmap = QPixmap(kpi_data.icon_path)
        self.icon_label.setPixmap(self.icon_pixmap.scaled(50, 50, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        self.icon_label.setAlignment(Qt.AlignmentFlag.AlignRight)

        self.value_layout.addWidget(self.value_label)
        self.value_layout.addWidget(self.icon_label)

        self.unit_label = QLabel(kpi_data.unit)
        self.unit_label.setFont(QFont('Arial', 10))
        self.unit_label.setAlignment(Qt.AlignmentFlag.AlignLeft)

        self.main_layout.addLayout(self.value_layout)
        self.main_layout.addWidget(self.unit_label)

        self.setLayout(self.main_layout)

    def update_kpi(self, kpi_data: KPIData):
        self.value_label.setText("{:,}".format(kpi_data.value))
        self.unit_label.setText(kpi_data.unit)
        self.icon_pixmap = QPixmap(kpi_data.icon_path)
        self.icon_label.setPixmap(self.icon_pixmap.scaled(50, 50, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))


