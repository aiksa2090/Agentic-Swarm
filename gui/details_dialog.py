from PySide6.QtWidgets import QDialog, QVBoxLayout, QTextBrowser, QPushButton, QHBoxLayout, QLabel
from PySide6.QtCore import Qt, QSize

class DetailsDialog(QDialog):
    def __init__(self, title, content, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.resize(800, 600)
        self.setMinimumSize(400, 300)
        
        # تفعيل أزرار التكبير والتصغير وتغيير الحجم
        self.setWindowFlags(
            Qt.Window | 
            Qt.CustomizeWindowHint | 
            Qt.WindowTitleHint | 
            Qt.WindowSystemMenuHint | 
            Qt.WindowMinimizeButtonHint | 
            Qt.WindowMaximizeButtonHint | 
            Qt.WindowCloseButtonHint
        )
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        
        # متصفح النص الغني (HTML)
        self.browser = QTextBrowser()
        self.browser.setHtml(content)
        self.browser.setOpenExternalLinks(True)
        self.browser.setStyleSheet("background-color: #111b21; border-radius: 10px; padding: 10px;")
        
        layout.addWidget(self.browser)
        
        # زر الإغلاق السفلي
        footer = QHBoxLayout()
        close_btn = QPushButton("إغلاق (X)")
        close_btn.setFixedWidth(100)
        close_btn.clicked.connect(self.close)
        close_btn.setStyleSheet("background-color: #ef4444; color: white; border-radius: 5px; padding: 5px;")
        
        footer.addStretch()
        footer.addWidget(close_btn)
        layout.addLayout(footer)
