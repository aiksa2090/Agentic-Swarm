import time
import logging
import json
import os
from backend.ai_engine import generate_agent_response
from backend.database import save_message, update_draft

logger = logging.getLogger(__name__)

# ============================================================================
#  أدوار الخبراء الافتراضية (يمكن تخصيصها من الواجهة)
# ============================================================================
DEFAULT_AGENTS_CONFIG = [
    {"id": 1, "role": "مهندس معماري للأنظمة: حلل الفكرة وضع الهيكلية الأساسية والتقنيات المطلوبة بطريقة عملية وجديدة.", "name": "🏗️ المهندس المعماري", "enabled": True, "model_tag": "google/gemma-4-e2b-it"},
    {"id": 2, "role": "مبرمج خبير: اقترح الأكواد والمنطق البرمجي، وقم بتحسين أي خلل ذكره المهندس السابق.", "name": "💻 المبرمج الخبير", "enabled": True, "model_tag": "google/gemma-4-e4b-it"},
    {"id": 3, "role": "خبير أمن سيبراني ومختبر اختراق: انتقد الهيكلية، واستخرج أضعف نقاطها الأمنية وحسنها بشراسة.", "name": "🛡️ خبير الأمن السيبراني", "enabled": True, "model_tag": "google/gemma-4-26b-a4b-it"},
    {"id": 4, "role": "مهندس جودة وتجربة مستخدم (QA): اطرح سيناريوهات فشل للنظام، وابحث عن ثغرات في التصميم وانتقدها وحلها.", "name": "🧪 مهندس الجودة (QA)", "enabled": True, "model_tag": "google/gemma-4-31b-it"},
    {"id": 5, "role": "كاتب وموثق تقني: قم بصياغة استنتاجات الفريق أعلاه في وثيقة مقروءة ومرتبة، وحرضهم للتطوير أكثر في الدورة القادمة.", "name": "📝 الكاتب التقني", "enabled": True, "model_tag": "google/gemma-4-e2b-it"}
]

CONFIG_DIR = "config"
CURRENT_CONFIG_PATH = os.path.join(CONFIG_DIR, "current_config.json")
TEMPLATES_PATH = os.path.join(CONFIG_DIR, "templates.json")
SETTINGS_PATH = os.path.join(CONFIG_DIR, "settings.json")

def ensure_config_dir():
    if not os.path.exists(CONFIG_DIR):
        os.makedirs(CONFIG_DIR)

def load_active_config():
    ensure_config_dir()
    if os.path.exists(CURRENT_CONFIG_PATH):
        try:
            with open(CURRENT_CONFIG_PATH, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            pass
    return [dict(a) for a in DEFAULT_AGENTS_CONFIG]

# التخصيص النشط حالياً
AGENTS_CONFIG = load_active_config()

def save_active_config():
    ensure_config_dir()
    with open(CURRENT_CONFIG_PATH, 'w', encoding='utf-8') as f:
        json.dump(AGENTS_CONFIG, f, ensure_ascii=False, indent=4)

def update_agents_config(new_config):
    """تحديث تخصيص الوكلاء من الواجهة"""
    global AGENTS_CONFIG
    AGENTS_CONFIG = []
    for agent_data in new_config:
        agent_id = int(agent_data["id"])
        # البحث عن القيم الافتراضية إذا نقصت
        default = next((a for a in DEFAULT_AGENTS_CONFIG if a["id"] == agent_id), {})
        
        AGENTS_CONFIG.append({
            "id": agent_id,
            "role": agent_data.get("role", default.get("role", "")),
            "name": agent_data.get("name", default.get("name", "")),
            "enabled": agent_data.get("enabled", default.get("enabled", True)),
            "model_tag": agent_data.get("model_tag", default.get("model_tag", "google/gemma-4-e2b-it"))
        })
    save_active_config()
    logger.info(f"Agents config updated and saved.")

def get_settings():
    ensure_config_dir()
    if os.path.exists(SETTINGS_PATH):
        try:
            with open(SETTINGS_PATH, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            pass
    return {"ai_customizer_model": "google/gemma-4-31b-it"}

def save_settings(settings):
    ensure_config_dir()
    with open(SETTINGS_PATH, 'w', encoding='utf-8') as f:
        json.dump(settings, f, ensure_ascii=False, indent=4)

def get_templates():
    ensure_config_dir()
    if os.path.exists(TEMPLATES_PATH):
        try:
            with open(TEMPLATES_PATH, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            pass
    return {}

def save_template(name, config):
    templates = get_templates()
    templates[name] = config
    with open(TEMPLATES_PATH, 'w', encoding='utf-8') as f:
        json.dump(templates, f, ensure_ascii=False, indent=4)

def delete_template(name):
    templates = get_templates()
    if name in templates:
        del templates[name]
        with open(TEMPLATES_PATH, 'w', encoding='utf-8') as f:
            json.dump(templates, f, ensure_ascii=False, indent=4)


def get_agents_config():
    """إرجاع التخصيص الحالي"""
    return AGENTS_CONFIG

def reset_agents_config():
    """إعادة التعيين للافتراضي"""
    global AGENTS_CONFIG
    AGENTS_CONFIG = [dict(a) for a in DEFAULT_AGENTS_CONFIG]
    save_active_config()

# قاموس لحفظ حالة الجلسات (للتحكم بالإيقاف المؤقت والإلغاء)
active_sessions_control = {}
# قاموس لجمع تدخلات وأوامر المستخدم الحية أثناء عمل الاستشاريين
active_sessions_interventions = {}

MAX_HISTORY_MESSAGES = 10 # الحفاظ على آخر دورتين تفاديا لتخطي الـ Context Window

def run_swarm_session(session_id: str, topic: str, stream_callback=None):
    """
    نظام الإدارة المركزي للمحادثة المتسلسلة التوازية (حلقة لا نهائية)
    """
    active_sessions_control[session_id] = "running"
    
    # سجل الحوار الأولي
    conversation_history = []
    
    current_prompt = f"الفكرة الرئيسية للمشروع هي: {topic}. قم بعملك وابدأ التحليل، أو انتقد وحسن ما سبق إذا كانت هذه الجولة متقدمة."
    
    cycle_number = 1
    
    while active_sessions_control.get(session_id) not in ["stopped", "finished"]:
        logger.info(f"--- بدء دورة تفكير المنسق (خلفية صامتة) رقم {cycle_number} ---")
        
        for agent in AGENTS_CONFIG:
            agent_id = agent["id"]
            role = agent["role"]
            enabled = agent.get("enabled", True)
            model_tag = agent.get("model_tag", "google/gemma-4-e2b-it")
            
            if not enabled:
                logger.info(f"Skipping Agent {agent_id} ({agent.get('name')}) - DISABLED")
                continue
            
            logger.info(f"Agent {agent_id} is running with model: {model_tag}")
            
            # فحص حالة التحكم (Start/Pause/Stop)
            while active_sessions_control.get(session_id) == "paused":
                time.sleep(1)
            
            if active_sessions_control.get(session_id) in ["stopped", "finished"]:
                if stream_callback:
                    stream_callback({"type": "info", "message": "تم إيقاف تشغيل العقل الجماعي بناءً على طلبك."})
                return
                
            # فحص ما إذا كان هناك أوامر حية من المستخدم (Manager Intervention)
            if session_id in active_sessions_interventions and len(active_sessions_interventions[session_id]) > 0:
                user_msg = "\n".join(active_sessions_interventions[session_id])
                current_prompt += f"\n\n[أمر وتوجيه عاجل من المدير - المستخدم البشري]: '{user_msg}'\nيجب عليكم حالاً قراءة وتطبيق توجيهات المدير وأخذها بعين الاعتبار في نقاشكم الحالي."
                active_sessions_interventions[session_id].clear()
                
            if stream_callback:
                stream_callback({"type": "status", "agent_id": agent_id, "status": "thinking"})
            
            # اقتطاع الذاكرة لتفادي انفجارها (Context Truncation)
            working_history = conversation_history[-MAX_HISTORY_MESSAGES:] if len(conversation_history) > MAX_HISTORY_MESSAGES else conversation_history
            
            # تشغيل الوكيل واستقبال الرد الكامل
            response = generate_agent_response(
                agent_id=agent_id,
                model_tag=model_tag,
                agent_role=role,
                conversation_history=working_history,
                new_prompt=current_prompt,
                stream_callback=stream_callback
            )
            
            # حفظ في قاعدة البيانات وسجل التاريخ الحي
            save_message(session_id=session_id, agent_id=agent_id, role="model", content=response)
            
            if stream_callback:
                stream_callback({"type": "status", "agent_id": agent_id, "status": "idle"})
            
            conversation_history.append({"role": "user", "content": current_prompt})
            conversation_history.append({"role": "model", "content": response})
            
            # توابع التطوير: الوكيل التالي يُطلب منه البناء والانتقاد
            current_prompt = f"[أهمية قصوى: بناءً على الفكرة الأصلية `{topic}`]\n راجع مخرجات وانتقادات الخبير السابق (رقم {agent_id})، ثم قم بتعزيز الفكرة ونقدها وتصنيفها من منظور احترافي لتصبح أفضل."

            if agent_id == 5:
                update_draft(session_id, response)
        
        cycle_number += 1
        time.sleep(2)
