import logging
from PySide6.QtWidgets import QDialog, QVBoxLayout, QPlainTextEdit, QPushButton, QHBoxLayout, QLabel
from PySide6.QtCore import Qt, Signal, QObject
from PySide6.QtGui import QTextCursor, QFont

class LogSignal(QObject):
    signal = Signal(str)

class DiagnosisHandler(logging.Handler):
    def __init__(self, log_signal):
        super().__init__()
        self.log_signal = log_signal

    def emit(self, record):
        msg = self.format(record)
        self.log_signal.signal.emit(msg)

class DiagnosisDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("أداة التشخيص المتقدمة - System Diagnosis")
        self.resize(900, 600)
        
        self.setWindowFlags(
            Qt.Window | 
            Qt.WindowMinimizeButtonHint | 
            Qt.WindowMaximizeButtonHint | 
            Qt.WindowCloseButtonHint
        )

        layout = QVBoxLayout(self)
        
        header = QLabel("📡 سجل الأخطاء والعمليات الحية (Live Logs & Traces)")
        header.setStyleSheet("font-weight: bold; font-size: 16px; color: #ec4899;")
        layout.addWidget(header)

        self.log_view = QPlainTextEdit()
        self.log_view.setReadOnly(True)
        self.log_view.setFont(QFont("Consolas", 10))
        self.log_view.setStyleSheet("background-color: #0b141a; color: #00ff00; border: 1px solid #202c33; border-radius: 5px;")
        layout.addWidget(self.log_view)

        btn_layout = QHBoxLayout()
        
        copy_btn = QPushButton("📋 نسخ السجل لإرساله للمبرمج")
        copy_btn.clicked.connect(self.copy_logs)
        copy_btn.setStyleSheet("background-color: #6366f1; color: white; padding: 10px; font-weight: bold;")
        
        clear_btn = QPushButton("🗑️ مسح")
        clear_btn.clicked.connect(self.log_view.clear)
        clear_btn.setFixedWidth(80)
        
        btn_layout.addWidget(copy_btn)
        btn_layout.addStretch()
        btn_layout.addWidget(clear_btn)
        
        layout.addLayout(btn_layout)

    def append_log(self, text):
        self.log_view.appendPlainText(text)
        self.log_view.moveCursor(QTextCursor.End)

    def copy_logs(self):
        from PySide6.QtGui import QGuiApplication
        clipboard = QGuiApplication.clipboard()
        clipboard.setText(self.log_view.toPlainText())

    def closeEvent(self, event):
        # بدلاً من تدمير النافذة، نقوم فقط بإخفائها ليرى المستخدم السجل القديم عند فتحها مرة أخرى
        self.hide()
        event.ignore()
