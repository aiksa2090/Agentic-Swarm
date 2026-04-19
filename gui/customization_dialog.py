import json
import os
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QTextEdit, QPushButton, QScrollArea, QWidget, QFrame,
    QListWidget, QMessageBox, QFileDialog, QComboBox, QCheckBox
)
from PySide6.QtCore import Qt, Signal
from gui.ai_worker import CustomizationWorker
from gui.components import AutoExpandingTextEdit
import backend.orchestrator as orchestrator
from backend.ai_engine import AVAILABLE_MODELS

class CustomizationDialog(QDialog):
    config_applied = Signal()
    live_change = Signal(int, dict) # agent_id, data

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("🎛️ تخصيص النماذج والوكلاء المتقدم")
        self.setMinimumSize(1000, 700)
        self.setLayoutDirection(Qt.RightToLeft)
        
        # تفعيل ملء الشاشة والتحكم الكامل
        self.setWindowFlags(Qt.Window | Qt.WindowMaximizeButtonHint | Qt.WindowCloseButtonHint)
        self.setStyleSheet("""
            QDialog { background-color: #0b141a; color: #e9edef; }
            QLabel { color: #e9edef; font-weight: bold; }
            QLineEdit, QTextEdit { 
                background-color: #2a3942; 
                border-radius: 5px; 
                padding: 10px; 
                color: #e9edef; 
                border: 1px solid #202c33;
            }
            QPushButton { 
                background-color: #202c33; 
                color: #e9edef; 
                border-radius: 5px; 
                padding: 8px 15px; 
                font-weight: bold; 
            }
            QPushButton:hover { background-color: #2a3942; }
            QListWidget { background-color: #111b21; border: none; color: #e9edef; }
            QListWidget::item { padding: 10px; border-bottom: 1px solid #202c33; }
            QListWidget::item:selected { background-color: #2a3942; color: #00a884; }
        """)
        
        self.worker = None
        self.current_agent_edits = {} # {id: {"name": QLineEdit, "role": QTextEdit, "model": QComboBox, "enabled": QCheckBox}}
        
        self.init_ui()
        self.load_data()

    def init_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # --- القائمة الجانبية (Templates & Actions) ---
        sidebar = QFrame()
        sidebar.setFixedWidth(280)
        sidebar.setStyleSheet("background-color: #111b21; border-left: 1px solid #202c33;")
        sidebar_layout = QVBoxLayout(sidebar)
        
        sidebar_layout.addWidget(QLabel("📂 القوالب المحفوظة"))
        self.template_list = QListWidget()
        self.template_list.itemDoubleClicked.connect(self.load_selected_template)
        sidebar_layout.addWidget(self.template_list)
        
        btn_save_tpl = QPushButton("💾 حفظ كقالب جديد")
        btn_save_tpl.clicked.connect(self.save_new_template)
        sidebar_layout.addWidget(btn_save_tpl)
        
        btn_del_tpl = QPushButton("🗑️ حذف القالب")
        btn_del_tpl.clicked.connect(self.delete_selected_template)
        sidebar_layout.addWidget(btn_del_tpl)
        
        sidebar_layout.addSpacing(20)
        sidebar_layout.addWidget(QLabel("📤 استيراد/تصدير"))
        
        btn_export = QPushButton("📤 تصدير إلى TXT")
        btn_export.clicked.connect(self.export_to_txt)
        sidebar_layout.addWidget(btn_export)
        
        btn_import = QPushButton("📥 استيراد من TXT")
        btn_import.clicked.connect(self.import_from_txt)
        sidebar_layout.addWidget(btn_import)
        
        sidebar_layout.addStretch()
        
        btn_close = QPushButton("✕ إغلاق")
        btn_close.clicked.connect(self.close)
        btn_close.setStyleSheet("background-color: #ef4444; color: white; padding: 10px; font-weight: bold;")
        sidebar_layout.addWidget(btn_close)
        
        layout.addWidget(sidebar)
        
        # --- اللوحة الرئيسية (Editors) ---
        main_editor = QFrame()
        main_editor_layout = QVBoxLayout(main_editor)
        
        header = QLabel("⚙️ تحرير أدوار ومهمات الفريق")
        header.setStyleSheet("font-size: 20px; font-weight: bold; color: #00a884; padding: 10px;")
        main_editor_layout.addWidget(header)
        
        # منطقة التخصيص بالذكاء الاصطناعي
        ai_frame = QFrame()
        ai_frame.setStyleSheet("background-color: #202c33; border-radius: 10px; padding: 10px; margin-bottom: 10px;")
        ai_layout = QVBoxLayout(ai_frame)
        ai_layout.addWidget(QLabel("🤖 تخصيص بالذكاء الاصطناعي (gemma-4-31b-it)"))
        
        self.ai_prompt = AutoExpandingTextEdit(min_height=60, max_height=120)
        self.ai_prompt.setPlaceholderText("مثلاً: اريد ان يكون متخصصون في البحار ومكافحة القرصنة...")
        ai_layout.addWidget(self.ai_prompt)
        
        ai_opt_layout = QHBoxLayout()
        ai_opt_layout.addWidget(QLabel("النموذج المستخدم للتخصيص:"))
        self.ai_customizer_select = QComboBox()
        self.ai_customizer_select.addItems(AVAILABLE_MODELS)
        self.ai_customizer_select.setCurrentText("google/gemma-4-31b-it") # الافتراضي
        ai_opt_layout.addWidget(self.ai_customizer_select)
        ai_layout.addLayout(ai_opt_layout)
        
        ai_btn_row = QHBoxLayout()
        btn_ai_all = QPushButton("🤖 بدء تخصيص الكل")
        btn_ai_all.clicked.connect(lambda: self.run_ai_customization(all_agents=True))
        btn_ai_all.setStyleSheet("background-color: #3b82f6; color: white; font-weight: bold;")
        
        self.ai_status = QLabel("جاهز")
        ai_btn_row.addWidget(btn_ai_all)
        ai_btn_row.addStretch()
        ai_btn_row.addWidget(self.ai_status)
        ai_layout.addLayout(ai_btn_row)
        
        main_editor_layout.addWidget(ai_frame)
        
        # منطقة تحرير الوكلاء الـ 5
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("border: none; background-color: transparent;")
        
        container = QWidget()
        self.agents_layout = QVBoxLayout(container)
        
        for i in range(1, 6):
            agent_box = QFrame()
            agent_box.setProperty("class", "AgentEditBox")
            ab_layout = QVBoxLayout(agent_box)
            
            agent_title = QLabel(f"<b>الوكيل رقم #{i}</b>")
            agent_title.setObjectName("AgentBucketTitle")
            ab_layout.addWidget(agent_title)
            
            name_edit = AutoExpandingTextEdit(min_height=35, max_height=70)
            name_edit.setPlaceholderText("اسم الدور (مثلاً: المبرمج)")
            ab_layout.addWidget(QLabel("اسم الدور:"))
            ab_layout.addWidget(name_edit)
            
            role_edit = AutoExpandingTextEdit(min_height=60, max_height=150)
            role_edit.setPlaceholderText("تعليمات الدور (System Prompt)...")
            ab_layout.addWidget(QLabel("تعليمات الدور:"))
            ab_layout.addWidget(role_edit)

            model_row = QHBoxLayout()
            model_row.addWidget(QLabel("تعيين النموذج:"))
            model_select = QComboBox()
            model_select.addItems(AVAILABLE_MODELS)
            model_row.addWidget(model_select)
            
            enabled_check = QCheckBox("تفعيل الوكيل")
            enabled_check.setChecked(True)
            model_row.addStretch()
            model_row.addWidget(enabled_check)
            ab_layout.addLayout(model_row)
            
            self.current_agent_edits[i] = {
                "name": name_edit, 
                "role": role_edit, 
                "model": model_select,
                "enabled": enabled_check
            }
            
            # توصيل الإشارات للتحديث اللحظي (Live Preview)
            agent_id = i
            name_edit.textChanged.connect(lambda _, aid=agent_id: self.emit_live_update(aid))
            model_select.currentIndexChanged.connect(lambda _, aid=agent_id: self.emit_live_update(aid))
            enabled_check.stateChanged.connect(lambda _, aid=agent_id: self.emit_live_update(aid))
            
            self.agents_layout.addWidget(agent_box)
            
        scroll.setWidget(container)
        main_editor_layout.addWidget(scroll)
        
        # أزرار الحفظ والاعتماد
        footer = QHBoxLayout()
        btn_apply = QPushButton("✅ تطبيق التخصيص وحفظه")
        btn_apply.clicked.connect(self.apply_and_save)
        btn_apply.setStyleSheet("background-color: #00a884; color: white; padding: 15px; font-weight: bold; font-size: 16px;")
        
        btn_reset = QPushButton("🔄 استعادة الافتراضي")
        btn_reset.clicked.connect(self.reset_to_default)
        
        footer.addWidget(btn_reset)
        footer.addStretch()
        footer.addWidget(btn_apply)
        main_editor_layout.addLayout(footer)
        
        layout.addWidget(main_editor, 1)

    def emit_live_update(self, agent_id):
        # تجميع البيانات الحالية للوكيل وإرسالها للتحديث اللحظي في الخلفية
        data = {
            "name": self.current_agent_edits[agent_id]["name"].toPlainText(),
            "model_tag": self.current_agent_edits[agent_id]["model"].currentText(),
            "enabled": self.current_agent_edits[agent_id]["enabled"].isChecked()
        }
        self.live_change.emit(agent_id, data)

    def load_data(self):
        # تحميل الإعدادات الحالية للوكلاء
        config = orchestrator.get_agents_config()
        for agent in config:
            aid = agent["id"]
            if aid in self.current_agent_edits:
                self.current_agent_edits[aid]["name"].setPlainText(agent["name"])
                self.current_agent_edits[aid]["role"].setPlainText(agent["role"])
                self.current_agent_edits[aid]["model"].setCurrentText(agent.get("model_tag", AVAILABLE_MODELS[0]))
                self.current_agent_edits[aid]["enabled"].setChecked(agent.get("enabled", True))
        
        # تحميل إعدادات التخصيص
        settings = orchestrator.get_settings()
        self.ai_customizer_select.setCurrentText(settings.get("ai_customizer_model", "google/gemma-4-31b-it"))
        
        # تحميل قائمة القوالب
        self.refresh_template_list()

    def refresh_template_list(self):
        self.template_list.clear()
        templates = orchestrator.get_templates()
        for name in templates.keys():
            self.template_list.addItem(name)

    def save_new_template(self):
        from PySide6.QtWidgets import QInputDialog
        name, ok = QInputDialog.getText(self, "حفظ قالب", "اسم القالب الجديد:")
        if ok and name:
            config = []
            for i in range(1, 6):
                config.append({
                    "id": i,
                    "name": self.current_agent_edits[i]["name"].toPlainText(),
                    "role": self.current_agent_edits[i]["role"].toPlainText(),
                    "model_tag": self.current_agent_edits[i]["model"].currentText(),
                    "enabled": self.current_agent_edits[i]["enabled"].isChecked()
                })
            orchestrator.save_template(name, config)
            self.refresh_template_list()

    def load_selected_template(self):
        item = self.template_list.currentItem()
        if not item: return
        name = item.text()
        templates = orchestrator.get_templates()
        config = templates.get(name)
        if config:
            for agent in config:
                aid = agent["id"]
                if aid in self.current_agent_edits:
                    self.current_agent_edits[aid]["name"].setPlainText(agent["name"])
                    self.current_agent_edits[aid]["role"].setPlainText(agent["role"])
                    self.current_agent_edits[aid]["model"].setCurrentText(agent.get("model_tag", AVAILABLE_MODELS[0]))
                    self.current_agent_edits[aid]["enabled"].setChecked(agent.get("enabled", True))

    def delete_selected_template(self):
        item = self.template_list.currentItem()
        if not item: return
        name = item.text()
        orchestrator.delete_template(name)
        self.refresh_template_list()

    def run_ai_customization(self, all_agents=True):
        prompt = self.ai_prompt.toPlainText().strip()
        if not prompt:
            QMessageBox.warning(self, "تنبيه", "يرجى كتابة ما تريده من الذكاء الاصطناعي أولاً.")
            return
        
        customizer_model = self.ai_customizer_select.currentText()
        self.ai_status.setText(f"🤖 جاري التوليد باستخدام {customizer_model.split('--')[-1]}...")
        self.ai_status.setStyleSheet("color: #3b82f6;")
        
        self.worker = CustomizationWorker(prompt, [1, 2, 3, 4, 5], model_tag=customizer_model)
        self.worker.finished.connect(self.on_ai_finished)
        self.worker.error.connect(self.on_ai_error)
        self.worker.start()

    def on_ai_finished(self, result):
        self.ai_status.setText("✅ اكتمل التوليد")
        self.ai_status.setStyleSheet("color: #00a884;")
        
        # تحليل النتيجة (Parsing)
        # ===AGENT_1===
        # الاسم: ...
        # الدور: ...
        try:
            import re
            for i in range(1, 6):
                pattern = rf"===AGENT_{i}===.*?الاسم:\s*(.*?)\n.*?الدور:\s*(.*?)\n===END==="
                match = re.search(pattern, result + "\n===END===", re.DOTALL | re.IGNORECASE)
                if match:
                    name = match.group(1).strip()
                    role = match.group(2).strip()
                    self.current_agent_edits[i]["name"].setText(name)
                    self.current_agent_edits[i]["role"].setText(role)
        except Exception as e:
            QMessageBox.critical(self, "خطأ في التحليل", f"تعذر تحليل رد الذكاء الاصطناعي: {str(e)}")

    def on_ai_error(self, err):
        self.ai_status.setText("❌ فشل التوليد")
        self.ai_status.setStyleSheet("color: #ef4444;")
        QMessageBox.critical(self, "خطأ بايتون", f"فشل استدعاء الموديل: {err}")

    def apply_and_save(self):
        new_config = []
        for i in range(1, 6):
            new_config.append({
                "id": i,
                "name": self.current_agent_edits[i]["name"].toPlainText(),
                "role": self.current_agent_edits[i]["role"].toPlainText(),
                "model_tag": self.current_agent_edits[i]["model"].currentText(),
                "enabled": self.current_agent_edits[i]["enabled"].isChecked()
            })
        
        # حفظ الإعدادات العامة
        settings = {"ai_customizer_model": self.ai_customizer_select.currentText()}
        orchestrator.save_settings(settings)
        
        orchestrator.update_agents_config(new_config)
        self.config_applied.emit()
        QMessageBox.information(self, "نجاح", "تم تطبيق وحفظ التخصيص الجديد بنجاح.")
        self.accept()

    def reset_to_default(self):
        if QMessageBox.question(self, "تأكيد", "هل أنت متأكد من رغبتك في العودة للإعدادات الأصلية؟") == QMessageBox.Yes:
            orchestrator.reset_agents_config()
            self.load_data()

    def export_to_txt(self):
        path, _ = QFileDialog.getSaveFileName(self, "تصدير التخصيص", "", "Text Files (*.txt)")
        if path:
            data = orchestrator.get_agents_config()
            with open(path, 'w', encoding='utf-8') as f:
                f.write("=== AGENTIC SWARM CUSTOMIZATION EXPORT ===\n\n")
                for a in data:
                    f.write(f"AGENT #{a['id']}\nNAME: {a['name']}\nROLE: {a['role']}\n-------------------\n")
            QMessageBox.information(self, "تصدير", "تم التصدير بنجاح.")

    def import_from_txt(self):
        # تبسيطاً، سنقوم باستيراد ملف JSON إذا أراد المستخدم، أو مجرد توفير الواجهة
        QMessageBox.information(self, "تنبيه", "ميزة الاستيراد من نص حر قيد التطوير، يرجى استخدام القوالب المحفوظة حالياً.")
