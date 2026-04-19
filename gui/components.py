from PySide6.QtWidgets import QTextEdit, QSizePolicy
from PySide6.QtCore import Qt, Signal

class AutoExpandingTextEdit(QTextEdit):
    """
    مربع نص يتوسع تلقائياً مع المحتوى بدلاً من التمرير الداخلي.
    """
    def __init__(self, parent=None, min_height=40, max_height=400):
        super().__init__(parent)
        self.min_height = min_height
        self.max_height = max_height
        
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        
        self.textChanged.connect(self.adjust_height)
        self.document().documentLayout().documentSizeChanged.connect(self.adjust_height)
        self.adjust_height()

    def adjust_height(self):
        # حساب الطول المطلوب بناءً على محتوى المستند بدقة
        doc_height = self.document().size().height()
        margins = self.contentsMargins()
        # نستخدم 20 بكسل إضافية للهوامش الداخلية لضمان عدم ظهور شريط التمرير مبكراً
        new_height = doc_height + margins.top() + margins.bottom() + 20
        
        final_height = max(self.min_height, min(new_height, self.max_height))
        self.setFixedHeight(final_height)
        
        # التحكم في شريط التمرير لضمان عدم "ارتفاع" النص للأعلى
        if new_height > self.max_height:
            self.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        else:
            self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
            # التأكد من أن النص في البداية عند التمدد
            self.verticalScrollBar().setValue(0)

    def keyPressEvent(self, event):
        # السماح بـ Enter للإرسال إذا كان الوالد يدعم ذلك (مثل الدردشة)
        if event.key() == Qt.Key_Return and not (event.modifiers() & Qt.ShiftModifier):
            # إرسال إشارة للوالد أن الإرسال مطلوب
            self.parent().on_send_clicked() if hasattr(self.parent(), 'on_send_clicked') else None
            # إذا كان الوالد هو Frame، نبحث عن MainWindow
            parent_window = self.window()
            if hasattr(parent_window, 'on_send_clicked'):
                parent_window.on_send_clicked()
            return
        super().keyPressEvent(event)
