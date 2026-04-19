import sys
import os
import ctypes
from PySide6.QtWidgets import QApplication

# تهيئة قاعدة البيانات عند بدء التشغيل
from backend.database import init_db
from gui.main_window import MainWindow

def setup_windows_env():
    """هذا ضروري لجعل أيقونة البرنامج تظهر بشكل صحيح في شريط مهام الويندوز بدلاً من أيقونة بايثون الافتراضية"""
    if os.name == 'nt':
        myappid = 'mycompany.myproduct.subproduct.version' # يمكن وضع اسم شركتك هنا
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

def main():
    setup_windows_env()
    
    # تهيئة قاعدة بيانات SQLite (متزامنة بالكامل في النسخة الجديدة)
    init_db()
    
    # بناء تطبيق سطح المكتب
    app = QApplication(sys.argv)
    
    # إعداد الخط الافتراضي لدعم اللغة العربية بشكل جميل
    font = app.font()
    font.setFamily("Segoe UI")
    font.setPointSize(10)
    app.setFont(font)
    
    # عرض النافذة
    window = MainWindow()
    window.show()
    
    # بدء حلقة التنفيذ (Event Loop) الخاصة بـ PySide6
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
