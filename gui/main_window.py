import sys
import logging
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QTextBrowser, QLineEdit, QPushButton, QLabel, 
    QSplitter, QFrame, QScrollArea, QProgressBar, QDialog
)
from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtGui import QFont, QTextCursor, QIcon

from gui.details_dialog import DetailsDialog
from gui.customization_dialog import CustomizationDialog
from gui.diagnosis_dialog import DiagnosisDialog, DiagnosisHandler, LogSignal
from gui.ai_worker import SwarmWorker
from gui.models_data import MODELS_INFO
from gui.components import AutoExpandingTextEdit
import backend.database as db
from backend.orchestrator import get_agents_config, reset_agents_config, active_sessions_control
from gui.app_style import DARK_QSS

# إعداد المسجل العالمي لربطه بنافذة التشخيص
log_signal_emitter = LogSignal()

class AgentCard(QFrame):
    details_requested = Signal(int, str) # agent_id, model_tag
    toggle_requested = Signal(int, bool) # agent_id, is_enabled

    def __init__(self, agent_id, name, model_name, size, enabled, model_tag=""):
        super().__init__()
        self.setObjectName("AgentCard")
        self.agent_id = agent_id
        self.model_tag = model_tag
        
        layout = QVBoxLayout(self)
        
        # الترويسة
        header = QHBoxLayout()
        title = QLabel(f"#{agent_id} {name}")
        title.setObjectName("AgentCardTitle")
        title.setTextInteractionFlags(Qt.TextSelectableByMouse)
        header.addWidget(title)
        header.addStretch()
        layout.addLayout(header)
        
        # معلومات الموديل (المعرف الفني)
        info = QHBoxLayout()
        tag_label = QLabel(f"المعرف: {model_tag}")
        tag_label.setObjectName("AgentCardModel")
        tag_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        tag_label.setStyleSheet("color: #00a884; font-weight: bold;")
        info.addWidget(tag_label)
        layout.addLayout(info)
        
        self.enabled = enabled
        self.status_label = QLabel("الحالة: جاهز 💤")
        self.status_label.setObjectName("AgentStatusLabel")
        layout.addWidget(self.status_label)
        
        # أزرار التحكم
        btn_layout = QHBoxLayout()
        
        # زر التفعيل/الإيقاف (Switch Style)
        self.toggle_btn = QPushButton("ON" if enabled else "OFF")
        self.toggle_btn.setFixedWidth(50)
        self.update_toggle_style()
        self.toggle_btn.setCursor(Qt.PointingHandCursor)
        self.toggle_btn.clicked.connect(self.on_toggle_clicked)
        
        btn_details = QPushButton("التفاصيل")
        btn_details.setObjectName("CardDetailsBtn")
        btn_details.setCursor(Qt.PointingHandCursor)
        btn_details.clicked.connect(lambda: self.details_requested.emit(self.agent_id, self.model_tag))
        
        btn_layout.addWidget(self.toggle_btn)
        btn_layout.addStretch()
        btn_layout.addWidget(btn_details)
        layout.addLayout(btn_layout)
        
        if not enabled:
            self.setGraphicsEffect(None) # يمكن إضافة تعتيم هنا
            self.setStyleSheet(self.styleSheet() + "#AgentCard { opacity: 0.5; border: 1px solid #444; }")

    def update_toggle_style(self):
        if self.toggle_btn.text() == "ON":
            self.toggle_btn.setStyleSheet("background-color: #00a884; color: white; border-radius: 10px; font-weight: bold;")
        else:
            self.toggle_btn.setStyleSheet("background-color: #ef4444; color: white; border-radius: 10px; font-weight: bold;")

    def on_toggle_clicked(self):
        self.enabled = not self.enabled
        self.toggle_btn.setText("ON" if self.enabled else "OFF")
        self.update_toggle_style()
        self.toggle_requested.emit(self.agent_id, self.enabled)

    def update_card(self, data):
        """تحديث بيانات البطاقة فوراً (Live Preview)"""
        name = data.get("name", "")
        model_tag = data.get("model_tag", "")
        enabled = data.get("enabled", True)
        
        # تحديث الاسم والمعرف
        self.findChild(QLabel, "AgentCardTitle").setText(f"#{self.agent_id} {name}")
        self.findChild(QLabel, "AgentCardModel").setText(f"المعرف: {model_tag}")
        
        # تعتيم البطاقة إذا كانت معطلة
        self.setEnabled(enabled)
        self.setOpacity(1.0 if enabled else 0.5)

    def setOpacity(self, opacity):
        from PySide6.QtWidgets import QGraphicsOpacityEffect
        effect = QGraphicsOpacityEffect(self)
        effect.setOpacity(opacity)
        self.setGraphicsEffect(effect)

    def set_status(self, status):
        if status == "thinking":
            self.status_label.setText("الحالة: يفكر الآن... 🧠")
            self.status_label.setStyleSheet("color: #00a884;")
        else:
            self.status_label.setText("الحالة: جاهز 💤")
            self.status_label.setStyleSheet("color: #8696a0;")

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Agentic Swarm - نظام العقل الجماعي")
        self.resize(1280, 800)
        self.setStyleSheet(DARK_QSS)
        self.setLayoutDirection(Qt.RightToLeft)
        
        # المكونات الإضافية
        self.worker = None
        self.diag_dialog = DiagnosisDialog(self)
        self.agent_cards = {}
        self.current_agent_buffers = {}
        self.auto_scroll_enabled = True
        
        # ربط الـ Logging بالواجهة
        handler = DiagnosisHandler(log_signal_emitter)
        handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        logging.getLogger().addHandler(handler)
        log_signal_emitter.signal.connect(self.diag_dialog.append_log)
        
        self.init_ui()
        self.make_selectable(self)
        
        # مؤقت المسودة
        self.draft_timer = QTimer(self)
        self.draft_timer.timeout.connect(self.update_draft_display)
        self.draft_timer.start(3000)

    def init_ui(self):
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        outer_layout = QVBoxLayout(main_widget)
        outer_layout.setContentsMargins(0, 0, 0, 0)
        outer_layout.setSpacing(0)
        
        # ========================================
        # 1. شريط التنقل العلوي (Navbar)
        # ========================================
        navbar = QFrame()
        navbar.setObjectName("Navbar")
        nav_layout = QHBoxLayout(navbar)
        
        # يمين الشريط (العنوان)
        title_label = QLabel("🧠 العقل الجماعي (Agentic Swarm)")
        title_label.setStyleSheet("font-weight: bold; font-size: 18px; margin-left: 10px;")
        nav_layout.addWidget(title_label)
        nav_layout.addStretch()
        
        # أزرار التحكم (مثل الصورة)
        self.btn_diag = QPushButton("🛡️ التشخيص")
        self.btn_diag.setObjectName("BtnDiagnosis")
        self.btn_diag.setProperty("class", "NavBtn")
        self.btn_diag.clicked.connect(self.diag_dialog.show)
        
        self.btn_models_view = QPushButton("📁 النماذج")
        self.btn_models_view.setObjectName("BtnModels")
        self.btn_models_view.setProperty("class", "NavBtn")
        
        self.btn_export = QPushButton("📥 تصدير المسودة")
        self.btn_export.setObjectName("BtnExport")
        self.btn_export.setProperty("class", "NavBtn")
        
        self.btn_restart = QPushButton("🔄 البدء من جديد")
        self.btn_restart.setObjectName("BtnRestart")
        self.btn_restart.setProperty("class", "NavBtn")
        
        self.btn_stop = QPushButton("🛑 إيقاف كلي")
        self.btn_stop.setObjectName("BtnStop")
        self.btn_stop.setProperty("class", "NavBtn")
        self.btn_stop.clicked.connect(self.stop_swarm)
        
        self.btn_pause = QPushButton("⏸ إيقاف مؤقت")
        self.btn_pause.setObjectName("BtnPause")
        self.btn_pause.setProperty("class", "NavBtn")
        self.btn_pause.clicked.connect(self.pause_swarm)
        
        self.btn_start = QPushButton("🚀 بدء")
        self.btn_start.setObjectName("BtnStart")
        self.btn_start.setProperty("class", "NavBtn")
        self.btn_start.clicked.connect(self.start_swarm)

        # زر المتابعة التلقائية
        self.btn_autoscroll = QPushButton("✓ متابعة تلقائية: ON")
        self.btn_autoscroll.setObjectName("AutoScrollBtn")
        self.btn_autoscroll.setProperty("active", "true")
        self.btn_autoscroll.setCheckable(True)
        self.btn_autoscroll.setChecked(True)
        self.btn_autoscroll.clicked.connect(self.toggle_autoscroll)
        
        nav_layout.addWidget(self.btn_diag)
        nav_layout.addWidget(self.btn_models_view)
        nav_layout.addWidget(self.btn_export)
        nav_layout.addWidget(self.btn_restart)
        nav_layout.addWidget(self.btn_stop)
        nav_layout.addWidget(self.btn_pause)
        nav_layout.addWidget(self.btn_start)
        nav_layout.addWidget(self.btn_autoscroll)
        
        outer_layout.addWidget(navbar)
        
        # ========================================
        # 2. منطقة Panels الثلاثية (Splitter)
        # ========================================
        splitter = QSplitter(Qt.Horizontal)
        
        # --- اللوحة اليمنى: قائمة الوكلاء ---
        right_panel = QFrame()
        right_panel.setObjectName("RightPanel")
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(5, 5, 5, 5)
        
        right_title = QLabel("👥 الفريق والخبراء")
        right_title.setObjectName("PanelTitle")
        # أزرار التخصيص والتحكم
        self.btn_customize = QPushButton("🎛️ تخصيص النماذج والوكلاء")
        self.btn_customize.setObjectName("BtnCustomize")
        self.btn_customize.clicked.connect(self.show_customization_dialog)
        self.btn_customize.setStyleSheet("""
            background-color: #3b82f6; 
            color: white; 
            padding: 10px; 
            font-weight: bold; 
            border-radius: 5px;
            margin: 5px;
        """)
        right_layout.addWidget(self.btn_customize)

        agent_scroll = QScrollArea()
        agent_scroll.setWidgetResizable(True)
        agent_container = QWidget()
        self.agent_cards_layout = QVBoxLayout(agent_container)
        self.agent_cards_layout.setAlignment(Qt.AlignTop)
        
        # إضافة بطاقات الوكلاء الـ 5
        self.setup_agent_cards()
        
        agent_scroll.setWidget(agent_container)
        right_layout.addWidget(agent_scroll)
        
        # --- اللوحة الوسطى: مجلس الاستشاريين (Chat) ---
        center_panel = QFrame()
        center_panel.setObjectName("CenterPanel")
        center_layout = QVBoxLayout(center_panel)
        
        center_title = QLabel("💬 مجلس الاستشاريين الذكي")
        center_title.setObjectName("PanelTitle")
        center_layout.addWidget(center_title)
        
        self.chat_box = QTextBrowser()
        self.chat_box.setTextInteractionFlags(Qt.TextSelectableByMouse | Qt.TextSelectableByKeyboard | Qt.LinksAccessibleByMouse)
        self.chat_box.setHtml("<p style='color: #8696a0; text-align: center;'>مرحباً بك.. أدخل فكرتك بالأسفل لتبدأ عملية العصف الذهني المحلي.</p>")
        center_layout.addWidget(self.chat_box)
        
        # منطقة الإدخال بالأسفل
        input_frame = QFrame()
        input_frame.setObjectName("InputFrame")
        input_layout = QHBoxLayout(input_frame)
        
        self.main_input = AutoExpandingTextEdit(min_height=40, max_height=150)
        self.main_input.setObjectName("MainInput")
        self.main_input.setPlaceholderText("اكتب فكرتك أو قدّم توجيهاتك هنا...")
        
        self.send_btn = QPushButton("➔")
        self.send_btn.setObjectName("SendBtn")
        self.send_btn.setFixedHeight(40)
        self.send_btn.clicked.connect(self.on_send_clicked)
        
        input_layout.addWidget(self.main_input)
        input_layout.addWidget(self.send_btn)
        center_layout.addWidget(input_frame)
        
        # --- اللوحة اليسرى: المسودة الحية ---
        left_panel = QFrame()
        left_panel.setObjectName("LeftPanel")
        left_layout = QVBoxLayout(left_panel)
        
        left_title = QLabel("📜 المسودة الحية الشاملة")
        left_title.setObjectName("PanelTitle")
        left_layout.addWidget(left_title)
        
        self.draft_box = QTextBrowser()
        self.draft_box.setTextInteractionFlags(Qt.TextSelectableByMouse | Qt.TextSelectableByKeyboard | Qt.LinksAccessibleByMouse)
        self.draft_box.setPlaceholderText("ستظهر هنا مسودة المشروع النهائية تدريجياً...")
        left_layout.addWidget(self.draft_box)
        
        # إضافة اللوحات للـ Splitter (الترتيب RTL: اليمين هو الأول في الكود)
        splitter.addWidget(right_panel)
        splitter.addWidget(center_panel)
        splitter.addWidget(left_panel)
        
        # ضبط الأحجام النسبية (20% | 55% | 25%)
        splitter.setSizes([250, 700, 330])
        
        outer_layout.addWidget(splitter, 1)

    def get_friendly_model_info(self, model_tag):
        """تحويل الـ Repo ID إلى اسم مألوف وحجم للمستخدم"""
        mapping = {
            "google/gemma-4-e2b-it": ("Gemma-4 2.6B (Edge)", "1.5GB"),
            "google/gemma-4-e4b-it": ("Gemma-4 4.4B (Small)", "3GB"),
            "google/gemma-4-26b-a4b-it": ("Gemma-4 26B (MoE)", "14GB"),
            "google/gemma-4-31b-it": ("Gemma-4 31B (Dense)", "16GB"),
            # أشكال بديلة للتاغات لضمان المطابقة
            "gemma-4-e2b-it": ("Gemma-4 2.6B (Edge)", "1.5GB"),
            "gemma-4-e4b-it": ("Gemma-4 4.4B (Small)", "3GB"),
            "gemma-4-26b-a4b-it": ("Gemma-4 26B (MoE)", "14GB"),
            "gemma-4-31b-it": ("Gemma-4 31B (Dense)", "16GB"),
        }
        return mapping.get(model_tag, (model_tag.split("/")[-1], "Unknown"))

    def refresh_agent_cards(self):
        """تحديث كافة البطاقات بناءً على الإعدادات الجديدة"""
        # مسح البطاقات القديمة
        for i in reversed(range(self.agent_cards_layout.count())): 
            self.agent_cards_layout.itemAt(i).widget().setParent(None)
        self.agent_cards = {}
        
        # إعادة بناء البطاقات
        self.setup_agent_cards()
        self.make_selectable(self) # إعادة تفعيل القابلية للنسخ للبطاقات الجديدة
        self.append_chat("🔄 تم تحديث إعدادات النماذج والوكلاء بنجاح.", color="#3b82f6")

    def setup_agent_cards(self):
        config = get_agents_config()
        for agent in config:
            aid = agent["id"]
            name = agent["name"]
            enabled = agent.get("enabled", True)
            model_tag = agent.get("model_tag", "google/gemma-4-e2b-it")
            
            # نستخدم المعرف الفني مباشرة كما طلب المستخدم
            card = AgentCard(aid, name, model_tag, "", enabled, model_tag=model_tag)
            card.details_requested.connect(self.show_model_details)
            card.toggle_requested.connect(self.on_agent_toggle)
            self.agent_cards[aid] = card
            self.agent_cards_layout.addWidget(card)

    def on_agent_toggle(self, agent_id, enabled):
        config = get_agents_config()
        for agent in config:
            if agent["id"] == agent_id:
                agent["enabled"] = enabled
                break
        from backend.orchestrator import save_active_config
        save_active_config()
        logging.info(f"Agent {agent_id} toggled to {'ENABLED' if enabled else 'DISABLED'}")

    def show_customization_dialog(self):
        diag = CustomizationDialog(self)
        self.make_selectable(diag) # جعل الدايلوج قابل للنسخ
        
        # الربط للتحديث اللحظي (Live Sync)
        diag.live_change.connect(self.update_card_preview)
        
        # عند إغلاق النافذة بنجاح، نقوم بتحديث الـ UI بالكامل
        diag.finished.connect(lambda r: self.refresh_agent_cards() if r == QDialog.Accepted else None)
        diag.exec()

    def update_card_preview(self, agent_id, data):
        """تحديث بطاقة الوكيل في الخلفية فوراً"""
        if agent_id in self.agent_cards:
            self.agent_cards[agent_id].update_card(data)

    def show_model_details(self, agent_id, model_tag):
        info = MODELS_INFO.get(model_tag)
        if info:
            diag = DetailsDialog(info["title"], info["content"], self)
            diag.exec()
        else:
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.warning(self, "تنبيه", f"لا توجد معلومات تقنية متاحة للنموذج: {model_tag}")

    def update_agent_status(self, agent_id: int, status: str):
        if agent_id in self.agent_cards:
            self.agent_cards[agent_id].set_status(status)

    def on_send_clicked(self):
        text = self.main_input.toPlainText().strip()
        if not text: return
        
        if self.worker and self.worker.isRunning():
            # هذا تدخل إداري
            self.worker.add_manager_intervention(text)
            self.append_chat(f"<b>[أنت - المدير]:</b> {text}", color="#a855f7")
        else:
            # بدء جلسة جديدة
            self.start_swarm_with_topic(text)
            
        self.main_input.clear()

    def start_swarm_with_topic(self, topic):
        self.append_chat(f"🚀 <b>بدء العصف الذهني:</b> {topic}", color="#00a884")
        self.worker = SwarmWorker(topic)
        self.worker.log_signal.connect(lambda t: logging.info(t))
        self.worker.status_signal.connect(self.update_agent_status)
        self.worker.token_signal.connect(self.on_token_received)
        self.worker.start()

    def start_swarm(self):
        # بدء يدوي من الزر (يستخدم ما في الحقل النصي)
        self.on_send_clicked()

    def stop_swarm(self):
        if self.worker:
            self.worker.stop_session()
            self.append_chat("🛑 تم طلب الإيقاف الكلي للجلسة.", color="#ef4444")
    def pause_swarm(self):
        if self.worker:
            if self.btn_pause.text() == "⏸ إيقاف مؤقت":
                self.worker.pause_session()
                self.btn_pause.setText("▶ استئناف")
            else:
                self.worker.resume_session()
                self.btn_pause.setText("⏸ إيقاف مؤقت")

    def toggle_autoscroll(self):
        self.auto_scroll_enabled = not self.auto_scroll_enabled
        self.btn_autoscroll.setText("✓ متابعة تلقائية: ON" if self.auto_scroll_enabled else "✕ متابعة تلقائية: OFF")
        self.btn_autoscroll.setProperty("active", "true" if self.auto_scroll_enabled else "false")
        self.btn_autoscroll.style().unpolish(self.btn_autoscroll)
        self.btn_autoscroll.style().polish(self.btn_autoscroll)

    def on_token_received(self, agent_id: int, token: str, bool_done: bool):
        if agent_id not in self.current_agent_buffers:
            name = get_agents_config()[agent_id-1]["name"]
            self.append_chat(f"<br><b style='color:#3b82f6;'>{name}:</b><br>")
            self.current_agent_buffers[agent_id] = True
            
        if token:
            if self.auto_scroll_enabled:
                self.chat_box.moveCursor(QTextCursor.End)
            self.chat_box.insertPlainText(token)
            
        if bool_done:
            # تم حذف الخط الأفقي <hr> تلبية لطلب المستخدم
            self.append_chat("<br>") 
            if agent_id in self.current_agent_buffers:
                del self.current_agent_buffers[agent_id]

    def append_chat(self, html, color=None):
        if self.auto_scroll_enabled:
            self.chat_box.moveCursor(QTextCursor.End)
        
        if color:
            self.chat_box.insertHtml(f"<div style='color:{color};'>{html}</div>")
        else:
            self.chat_box.insertHtml(html)
        
        if self.auto_scroll_enabled:
            self.chat_box.moveCursor(QTextCursor.End)

    def update_draft_display(self):
        if self.worker and self.worker.session_id:
            text = db.get_draft(self.worker.session_id)
            if text and text != self.draft_box.toPlainText():
                self.draft_box.setMarkdown(text)

    def show_diagnosis(self):
        diag = DiagnosisDialog(self)
        diag.exec()

    def make_selectable(self, widget):
        """تجعل كافة النصوص في الواجهة قابلة للتحديد بالماوس للنسخ مع الحفاظ على إمكانية الكتابة"""
        from PySide6.QtWidgets import QLabel, QTextBrowser, QTextEdit
        
        # إذا كان العنصر نفسه نصاً
        if isinstance(widget, QLabel):
            widget.setTextInteractionFlags(Qt.TextSelectableByMouse)
        
        # معالجة كافة الأبناء
        for child in widget.findChildren(QLabel):
            child.setTextInteractionFlags(Qt.TextSelectableByMouse)
            
        for child in widget.findChildren(QTextBrowser):
            # النصوص المتصفحة (Read-only)
            child.setTextInteractionFlags(Qt.TextSelectableByMouse | Qt.LinksAccessibleByMouse)
            
        for child in widget.findChildren(QTextEdit):
            # التأكد من عدم تعطيل الكتابة في مربعات الإدخال
            # نتحقق إذا كان العنصر ليس QTextBrowser (لأن QTextBrowser يرث من QTextEdit)
            if not isinstance(child, QTextBrowser):
                child.setTextInteractionFlags(Qt.TextSelectableByMouse | Qt.TextEditable | Qt.TextSelectableByKeyboard)
            else:
                child.setTextInteractionFlags(Qt.TextSelectableByMouse | Qt.LinksAccessibleByMouse)


    def closeEvent(self, event):
        if self.worker: self.worker.stop_session()
        event.accept()
