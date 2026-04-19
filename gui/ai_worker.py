import time
import uuid
from PySide6.QtCore import QThread, Signal
from backend.orchestrator import run_swarm_session, active_sessions_control, active_sessions_interventions
from backend.database import create_session
from backend.ai_engine import generate_ai_customization

class SwarmWorker(QThread):
    # إشارات (Signals) للاتصال مع خيط الواجهة المرئية بدون حظر أو تجميد
    log_signal = Signal(str)
    status_signal = Signal(int, str)
    token_signal = Signal(int, str, bool) # agent_id, token, done
    info_signal = Signal(str)
    
    def __init__(self, topic: str):
        super().__init__()
        self.topic = topic
        self.session_id = str(uuid.uuid4())
        
    def add_manager_intervention(self, message: str):
        """إضافة أمر صوته أعلى من باقي الوكلاء لكسر السياق"""
        if self.session_id not in active_sessions_interventions:
            active_sessions_interventions[self.session_id] = []
        active_sessions_interventions[self.session_id].append(message)
        
    def stream_callback(self, data: dict):
        """تستقبل الـ Callback من محرك AI وترمي Signal للواجهة"""""
        msg_type = data.get("type")
        if msg_type == "stream":
            self.token_signal.emit(data["agent_id"], data["token"], data.get("done", False))
        elif msg_type == "status":
            self.status_signal.emit(data["agent_id"], data["status"])
        elif msg_type == "system_info":
            self.log_signal.emit(f"[Agent {data['agent_id']}] {data['message']}")
        elif msg_type == "info":
            self.info_signal.emit(data["message"])

    def run(self):
        """حلقة QThread الآمنة - إذا تجمدت هنا فلن تتجمد الواجهة!"""
        self.log_signal.emit(f"يتم تحضير البيئة وإنشاء الخوادم للجلسة: {self.session_id}")
        create_session(self.session_id, self.topic)
        active_sessions_interventions[self.session_id] = []
        
        try:
            # تشغيل الدورة اللا نهائية
            run_swarm_session(self.session_id, self.topic, stream_callback=self.stream_callback)
        except Exception as e:
            self.log_signal.emit(f"خطأ فادح في خيط المعالجة: {str(e)}")
            
    def pause_session(self):
        active_sessions_control[self.session_id] = "paused"
        
    def resume_session(self):
        active_sessions_control[self.session_id] = "running"
        
    def stop_session(self):
        active_sessions_control[self.session_id] = "stopped"

class CustomizationWorker(QThread):
    finished = Signal(str)
    error = Signal(str)

    def __init__(self, user_prompt, agent_ids, model_tag="google/gemma-4-31b-it"):
        super().__init__()
        self.user_prompt = user_prompt
        self.agent_ids = agent_ids
        self.model_tag = model_tag

    def run(self):
        try:
            result = generate_ai_customization(self.user_prompt, self.agent_ids, self.model_tag)
            self.finished.emit(result)
        except Exception as e:
            self.error.emit(str(e))
