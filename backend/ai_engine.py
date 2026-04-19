# لا يوجد asyncio هنا بعد الآن
from transformers import AutoModelForCausalLM, AutoTokenizer, TextIteratorStreamer, BitsAndBytesConfig
from threading import Thread
import torch
import logging
import gc
import os
import warnings

# إخفاء تحذيرات Triton المزعجة على أنظمة ويندوز
warnings.filterwarnings("ignore", message=".*triton not found.*")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# جلب توكن HuggingFace من البيئة (تم استبعاده بناءً على طلب المستخدم)
# HF_TOKEN = os.environ.get("HF_TOKEN")

# ============================================================================
#  خريطة النماذج الأربعة لجهاز RTX 4090 Laptop (16GB VRAM + 32GB RAM)
# ============================================================================
#  النماذج يتم الاتصال بها من الكاش المحلي (لا يتم نقلها أو نسخها)
#  المسارات في الكاش:
#    C:\Users\USERNAME\.cache\huggingface\hub\models--google--gemma-4-e2b-it
#    C:\Users\USERNAME\.cache\huggingface\hub\models--google--gemma-4-e4b-it
#    C:\Users\USERNAME\.cache\huggingface\hub\models--google--gemma-4-26b-a4b-it
#    C:\Users\USERNAME\.cache\huggingface\hub\models--google--gemma-4-31b-it
#
#  استراتيجية التحميل:
#    E2B (2.6B)   → ~1.5GB 4-bit  → GPU فقط ✅
#    E4B (4.4B)   → ~3GB 4-bit    → GPU فقط ✅
#    26B-A4B (26.5B MoE) → ~13.3GB 4-bit → GPU مع حد 14GB ⚠️
#    31B (32.7B Dense)   → ~16.4GB 4-bit → GPU 14GB + CPU Offload ~2.4GB ⚠️
# ============================================================================

# خريطة الموديلات المتوفرة للاختيار
AVAILABLE_MODELS = [
    "google/gemma-4-e2b-it",
    "google/gemma-4-e4b-it",
    "google/gemma-4-26b-a4b-it",
    "google/gemma-4-31b-it"
]

# النماذج التي تحتاج تحديد حدود الذاكرة (أكبر من 10GB بعد الضغط)
LARGE_MODELS = {
    "google/gemma-4-26b-a4b-it",   # MoE ~13.3GB → يحتاج حد GPU
    "google/gemma-4-31b-it"        # Dense ~16.4GB → يحتاج CPU offload
}

def get_local_model_path(repo_id: str) -> str:
    """إرجاع المسار المحلي المطلق للموديل إذا كان موجوداً لتخطي أي اتصال بالإنترنت"""
    cache_dir = os.path.expanduser(r"~\.cache\huggingface\hub")
    folder_name = "models--" + repo_id.replace("/", "--")
    snapshots_dir = os.path.join(cache_dir, folder_name, "snapshots")
    if os.path.exists(snapshots_dir):
        subdirs = os.listdir(snapshots_dir)
        if subdirs:
            return os.path.join(snapshots_dir, subdirs[0])
    return repo_id

def load_engine():
    """إقلاع لحظي - لا نحمّل أي نموذج حتى يُطلب"""
    logger.info("Swarm Engine Initialized. Dynamic VRAM Mode is ACTIVE.")
    logger.info(f"Available models for selection: {AVAILABLE_MODELS}")
    if torch.cuda.is_available():
        gpu_name = torch.cuda.get_device_name(0)
        vram_total = torch.cuda.get_device_properties(0).total_memory / 1e9
        logger.info(f"GPU: {gpu_name}, VRAM: {vram_total:.1f}GB")
    else:
        logger.warning("No CUDA GPU detected! Models will run on CPU (very slow).")

def generate_agent_response(agent_id: int, model_tag: str, agent_role: str, conversation_history: list, new_prompt: str, stream_callback=None) -> str:
    """
    تحميل النموذج المختار → توليد الاستجابة → تفريغ الذاكرة بالكامل
    """
    repo_id = model_tag
    is_large = repo_id in LARGE_MODELS
    logger.info(f"[Agent {agent_id}] Loading {repo_id} ({'LARGE - CPU Offload enabled' if is_large else 'Standard'})...")
    
    if stream_callback:
        stream_callback({"type": "system_info", "agent_id": agent_id, "message": f"يتم استدعاء {repo_id} للذاكرة..."})

    # تفريغ الذاكرة تماماً قبل البدء لضمان أقصى مساحة للكارت
    gc.collect()
    if torch.cuda.is_available():
        torch.cuda.empty_cache()

    # ============================================================================
    #  ضغط 4-bit NF4 مع ضغط مزدوج لأقصى توفير في VRAM
    # ============================================================================
    quantization_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_compute_dtype=torch.bfloat16,
        bnb_4bit_use_double_quant=True,
        bnb_4bit_quant_type="nf4"
    )

    model = None
    tokenizer = None
    inputs = None
    
    try:
        local_path = get_local_model_path(repo_id)
        
        # === تحميل النموذج محلياً ===
        tokenizer = AutoTokenizer.from_pretrained(local_path, local_files_only=True)
        
        load_kwargs = {
            "quantization_config": quantization_config,
            "device_map": "auto",
            "offload_folder": "offload_dir",
            "low_cpu_mem_usage": True,
            "local_files_only": True
        }
        
        if is_large:
            load_kwargs["max_memory"] = {
                0: "14.5GiB", # تقليل الحد قليلاً لترك مساحة للنظام والواجهة
                "cpu": "16GiB" # زيادة مساحة الرام المسموحة للأوفلود الجيد   
            }
            logger.info(f"[Agent {agent_id}] Using max_memory limits: GPU=14.5GiB, CPU=16GiB. TurboQuant KV philosophy applied.")
        
        try:
            model = AutoModelForCausalLM.from_pretrained(local_path, **load_kwargs)
        except Exception as model_err:
            err_msg = f"\n[خطأ داخلي: فشل تحميل النموذج. {str(model_err)}]\n"
            logger.error(f"فشل التحميل للنموذج عبر المسار {local_path}: {str(model_err)}")
            if stream_callback:
                stream_callback({"type": "stream", "agent_id": agent_id, "token": err_msg, "done": True})
            return "[حدث خطأ أثناء محاولة تحميل النموذج]"
        
        if torch.cuda.is_available():
            used = torch.cuda.memory_allocated() / 1e9
            logger.info(f"[Agent {agent_id}] Model loaded. VRAM used: {used:.1f}GB")

        # === بناء المحادثة ===
        system_instruction = f"أنت خبير رقم {agent_id} مخصص لـ: {agent_role}. استخدم قدراتك لتحليل الأفكار باحترافية."
        
        chat = [{"role": "user", "content": system_instruction}]
        chat.extend(conversation_history)
        chat.append({"role": "user", "content": new_prompt})

        prompt_text = tokenizer.apply_chat_template(chat, tokenize=False, add_generation_prompt=True)
        
        # النماذج الكبيرة: لا نجبر الإدخال على GPU لأن جزءاً من النموذج قد يكون على CPU
        if is_large:
            inputs = tokenizer([prompt_text], return_tensors="pt").to(model.device)
        else:
            inputs = tokenizer([prompt_text], return_tensors="pt").to("cuda")
        
        # === التوليد بالبث المباشر ===
        streamer = TextIteratorStreamer(tokenizer, skip_prompt=True, skip_special_tokens=True)
        
        # النماذج الكبيرة: توليد أقصر لتوفير الوقت والذاكرة
        max_tokens = 400 if is_large else 600
        
        generation_kwargs = dict(
            **inputs,
            streamer=streamer,
            max_new_tokens=max_tokens,
            do_sample=True,
            temperature=0.7,
            top_p=0.9
        )
        
        def run_generate():
            try:
                with torch.no_grad():
                    model.generate(**generation_kwargs)
            except Exception as gen_err:
                logger.error(f"[Agent {agent_id}] Generation error: {gen_err}")

        thread = Thread(target=run_generate)
        thread.start()
        
        full_response = ""
        for new_text in streamer:
            full_response += new_text
            if stream_callback:
                stream_callback({"type": "stream", "agent_id": agent_id, "token": new_text, "done": False})
            
        if stream_callback:
            stream_callback({"type": "stream", "agent_id": agent_id, "token": "", "done": True})
        
        thread.join(timeout=60 if is_large else 30)

        return full_response

    except Exception as e:
        err = f"خطأ في استدعاء الذكاء (الوكيل {agent_id} - {repo_id}): {str(e)}"
        logger.error(err)
        if stream_callback:
            stream_callback({"type": "stream", "agent_id": agent_id, "token": err, "done": True})
        return err
    
    finally:
        # ============================================================================
        #  التفريغ النووي للذاكرة - يتم تنفيذه دائماً (finally block)
        # ============================================================================
        logger.info(f"[Agent {agent_id}] Purging {repo_id} from VRAM...")
        
        # 1. تحرير النموذج عبر accelerate
        if model is not None:
            try:
                from accelerate.utils import release_memory
                model = release_memory(model)
            except Exception:
                pass
            try:
                del model
            except Exception:
                pass
            model = None
        
        # 2. حذف باقي الكائنات
        if tokenizer is not None:
            del tokenizer
            tokenizer = None
        if inputs is not None:
            del inputs
            inputs = None
        
        # 3. تنظيف عميق
        gc.collect()
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
            torch.cuda.synchronize()
            free_vram = torch.cuda.mem_get_info()[0] / 1e9
            total_vram = torch.cuda.mem_get_info()[1] / 1e9
            logger.info(f"[Agent {agent_id}] Purge complete. Free VRAM: {free_vram:.1f}GB / {total_vram:.1f}GB")


def generate_ai_customization(user_prompt: str, agent_ids: list, model_tag: str = "google/gemma-4-31b-it") -> str:
    """
    استخدام نموذج مختار (الأفضل 31B) لتوليد تخصيصات ذكية للوكلاء
    يُرجع نصاً بتعليمات مخصصة لكل وكيل
    """
    repo_id = model_tag
    logger.info(f"[AI Customize] Loading {repo_id} for customization...")
    
    # تنظيف شامل للذاكرة قبل استدعاء "الوحش" 31B
    gc.collect()
    if torch.cuda.is_available():
        torch.cuda.empty_cache()

    quantization_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_compute_dtype=torch.bfloat16,
        bnb_4bit_use_double_quant=True,
        bnb_4bit_quant_type="nf4"
    )
    
    model = None
    tokenizer = None
    inputs = None
    
    try:
        local_path = get_local_model_path(repo_id)
        logger.info(f"[AI Customize] Loading {local_path} locally...")
        
        tokenizer = AutoTokenizer.from_pretrained(local_path, local_files_only=True)
        
        try:
            model = AutoModelForCausalLM.from_pretrained(
                local_path,
                quantization_config=quantization_config,
                device_map="auto",
                offload_folder="offload_dir",
                low_cpu_mem_usage=True,
                local_files_only=True,
                max_memory={0: "14.5GiB", "cpu": "16GiB"}
            )
        except Exception as model_init_err:
            logger.error(f"فشل تحميل النموذج {repo_id}: {str(model_init_err)}")
            if repo_id != "google/gemma-4-e2b-it":
                fallback = "google/gemma-4-e2b-it"
                logger.warning(f"محاولة التحويل التلقائي لنموذج بديل ومستقر: {fallback}")
                return generate_ai_customization(user_prompt, agent_ids, model_tag=fallback)
            raise Exception("تعذر تحميل أي نموذج لتخصيص الوكلاء.")
            
        
        agents_list = ", ".join([f"الوكيل {i}" for i in agent_ids])
        
        system_prompt = f"""أنت مساعد ذكي متخصص في تخصيص وكلاء الذكاء الاصطناعي.
المطلوب: بناءً على طلب المستخدم، قم بإنشاء تعليمات (System Prompts) مخصصة للوكلاء التالية: {agents_list}.

لكل وكيل يجب أن تُنتج:
1. اسم الدور الجديد (مع إيموجي مناسب)
2. وصف الدور التفصيلي (Role Description) — جملة شاملة توضح ما يفعله هذا الوكيل

أجب بالتنسيق التالي لكل وكيل:
===AGENT_[رقم]===
الاسم: [إيموجي] [اسم الدور]
الدور: [وصف تفصيلي شامل لما يفعله هذا الوكيل]
===END===

طلب المستخدم: {user_prompt}"""

        chat = [{"role": "user", "content": system_prompt}]
        prompt_text = tokenizer.apply_chat_template(chat, tokenize=False, add_generation_prompt=True)
        inputs = tokenizer([prompt_text], return_tensors="pt").to(model.device)
        
        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                max_new_tokens=800,
                do_sample=True,
                temperature=0.7,
                top_p=0.9
            )
        
        result = tokenizer.decode(outputs[0][inputs["input_ids"].shape[1]:], skip_special_tokens=True)
        logger.info(f"[AI Customize] Generated customization successfully.")
        return result
        
    except Exception as e:
        logger.error(f"[AI Customize] Error: {str(e)}")
        raise e
    
    finally:
        if model is not None:
            try:
                from accelerate.utils import release_memory
                model = release_memory(model)
            except: pass
            try: del model
            except: pass
        if tokenizer is not None: del tokenizer
        if inputs is not None: del inputs
        gc.collect()
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
            torch.cuda.synchronize()

