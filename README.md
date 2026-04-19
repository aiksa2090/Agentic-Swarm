<p align="center">
  <h1 align="center">🧠 Agentic Swarm</h1>
  <p align="center">
    <strong>نظام ذكاء اصطناعي متعدد الوكلاء يعمل محلياً بالكامل — Multi-Agent AI System Running 100% Offline</strong>
  </p>
  <p align="center">
    <a href="#-quick-start">Quick Start</a> •
    <a href="#-المتطلبات-requirements">Requirements</a> •
    <a href="#-النماذج-المستخدمة-models">Models</a> •
    <a href="#-الاستخدام-usage">Usage</a> •
    <a href="#-البنية-المعمارية-architecture">Architecture</a>
  </p>
  <p align="center">
    <img src="https://img.shields.io/badge/Python-3.13-blue?logo=python&logoColor=white" alt="Python">
    <img src="https://img.shields.io/badge/PySide6-Qt%206-41CD52?logo=qt&logoColor=white" alt="PySide6">
    <img src="https://img.shields.io/badge/PyTorch-2.x+cu126-EE4C2C?logo=pytorch&logoColor=white" alt="PyTorch">
    <img src="https://img.shields.io/badge/CUDA-12.6-76B900?logo=nvidia&logoColor=white" alt="CUDA">
    <img src="https://img.shields.io/badge/Gemma--4-Google%20DeepMind-4285F4?logo=google&logoColor=white" alt="Gemma-4">
    <img src="https://img.shields.io/badge/License-Apache%202.0-green" alt="License">
    <img src="https://img.shields.io/badge/Status-Offline--First-brightgreen" alt="Status">
  </p>
</p>

---

## 📖 نظرة عامة — Overview

**Agentic Swarm** هو تطبيق سطح مكتب أصلي (Native Desktop Application) مبني بـ Python و PySide6، يُدير **فريقاً من 5 وكلاء ذكاء اصطناعي** يعملون بشكل تعاوني ومتسلسل في **حلقة لا نهائية** للعصف الذهني وتطوير الأفكار.

**Agentic Swarm** is a native desktop application built with Python & PySide6 that orchestrates a **team of 5 AI agents** working collaboratively in an **infinite loop** for brainstorming and iterative idea development. It runs **100% offline** on your local hardware using Google's Gemma-4 model family.

### ✨ أبرز المميزات — Key Features

| الميزة | الوصف |
|--------|-------|
| 🔒 **Offline-First** | يعمل بالكامل بدون إنترنت بعد تحميل النماذج |
| 🧠 **5 AI Agents** | 5 وكلاء متخصصين يتعاونون في حلقة لا نهائية |
| ⚡ **4-bit Quantization** | ضغط NF4 مع ضغط مزدوج لأقصى توفير في VRAM |
| 🔄 **Dynamic VRAM Swapping** | مبادلة ذكية: حمّل → ولّد → فرّغ لكل وكيل |
| 🎨 **WhatsApp-Style UI** | واجهة رسومية أنيقة بتصميم مستوحى من WhatsApp Dark |
| 📡 **Live Streaming** | بث التوكنات حرفاً حرفاً في الوقت الفعلي |
| 🤖 **AI Customization** | تخصيص الوكلاء بالذكاء الاصطناعي أو يدوياً |
| 👤 **Human-in-the-Loop** | تدخل بشري حي أثناء عمل الوكلاء |
| 💾 **Templates System** | حفظ وتحميل قوالب تخصيص جاهزة |
| 🩺 **Live Diagnostics** | سجل تشخيصي حي لمراقبة الأداء |
| 🌐 **Full RTL Support** | دعم كامل للغة العربية (من اليمين لليسار) |

---

## 🖥️ لقطات الشاشة — Screenshots

> 📸 *سيتم إضافة لقطات شاشة قريباً*

---

## ⚡ Quick Start

```powershell
# 1. Clone the repository
git clone https://github.com/alka2090/Agentic-Swarm.git
cd Agentic-Swarm

# 2. Download at least one Gemma-4 model (smallest first)
pip install huggingface_hub
huggingface-cli login
huggingface-cli download google/gemma-4-e2b-it

# 3. Run the application
.\run_project.ps1
```

> ⚠️ يتطلب كرت شاشة NVIDIA بذاكرة 12GB+ — Requires NVIDIA GPU with 12GB+ VRAM

---

## 📋 المتطلبات — Requirements

### متطلبات الجهاز — Hardware Requirements

| المكوّن | الحد الأدنى | المثالي |
|---------|-------------|---------|
| **نظام التشغيل** | Windows 10 (64-bit) | Windows 11 |
| **كرت شاشة NVIDIA** | RTX 3060 (12GB VRAM) | RTX 4070+ (12GB+ VRAM) |
| **الذاكرة (RAM)** | 16GB DDR4 | 32GB DDR5 |
| **المعالج (CPU)** | Intel i5 / Ryzen 5 | Intel i9 / Ryzen 9 |
| **مساحة القرص** | 50GB فارغة | 100GB+ |
| **إنترنت** | مطلوب مرة واحدة للتثبيت | بعد التثبيت: لا يحتاج إنترنت |

### متطلبات البرمجيات — Software Requirements

| البرنامج | الإصدار | رابط التحميل | ملاحظة |
|---------|---------|-------------|--------|
| **Python** | 3.10+ | [python.org](https://www.python.org/downloads/) | ⚠️ فعّل "Add to PATH" أثناء التثبيت |
| **NVIDIA Driver** | 525+ | [nvidia.com](https://www.nvidia.com/Download/index.aspx) | أعد التشغيل بعد التثبيت |
| **CUDA Toolkit** | 12.4+ | [CUDA 12.6](https://developer.nvidia.com/cuda-12-6-0-download-archive) | اختر "Express Install" |
| **PyTorch** | 2.x+cu126 | [pytorch.org](https://pytorch.org/) | التثبيت عبر الأمر أدناه |

---

## 🔧 التثبيت الكامل — Full Installation Guide

### الخطوة 1: تثبيت Python

```powershell
# تحميل Python 3.13 من الموقع الرسمي
# ⚠️ أثناء التثبيت: فعّل خيار "Add python.exe to PATH"

# التحقق:
python --version
# المتوقع: Python 3.13.x
```

### الخطوة 2: تثبيت NVIDIA Driver + CUDA

```powershell
# 1. ثبّت أحدث تعريف NVIDIA من: https://www.nvidia.com/Download/index.aspx
# 2. أعد تشغيل الكمبيوتر
# 3. ثبّت CUDA Toolkit 12.6 من: https://developer.nvidia.com/cuda-12-6-0-download-archive

# التحقق:
nvidia-smi
nvcc --version
```

### الخطوة 3: تثبيت PyTorch مع دعم CUDA

```powershell
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu126
```

```powershell
# التحقق من أن PyTorch يرى كرت الشاشة:
python -c "import torch; print('CUDA:', torch.cuda.is_available()); print('GPU:', torch.cuda.get_device_name(0))"
# المتوقع: CUDA: True | GPU: NVIDIA GeForce RTX XXXX
```

### الخطوة 4: تحميل نماذج Gemma-4

```powershell
# تثبيت أداة HuggingFace
pip install huggingface_hub

# تسجيل الدخول (تحتاج حساب مجاني على huggingface.co)
huggingface-cli login
```

> ⚠️ **يجب قبول ترخيص كل نموذج** من صفحته على HuggingFace قبل التحميل (انظر قسم النماذج أدناه)

```powershell
# تحميل النماذج (ابدأ بالأصغر):
huggingface-cli download google/gemma-4-e2b-it      # ~5GB  — ابدأ بهذا
huggingface-cli download google/gemma-4-e4b-it      # ~9GB  — اختياري
huggingface-cli download google/gemma-4-26b-a4b-it  # ~28GB — اختياري
huggingface-cli download google/gemma-4-31b-it      # ~35GB — اختياري
```

### الخطوة 5: استنساخ وتشغيل المشروع

```powershell
# استنساخ المشروع
git clone https://github.com/alka2090/Agentic-Swarm.git
cd Agentic-Swarm

# السماح بتشغيل السكربتات (مرة واحدة فقط)
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned

# تشغيل البرنامج (يثبت المكتبات تلقائياً في أول مرة)
.\run_project.ps1
```

---

## 🤖 النماذج المستخدمة — Models

يستخدم المشروع نماذج **Google Gemma-4** المفتوحة المصدر (Apache 2.0) من **Google DeepMind**.

### 1️⃣ عائلة النماذج الطرفية — Edge-Optimized Family

تتميز بتقنية "Per-Layer Embeddings" (PLE) لزيادة الكفاءة على الأجهزة الصغيرة.

#### Gemma 4 E2B — النموذج الأخف والأسرع

| المواصفة | القيمة |
|----------|--------|
| **المعرف** | `google/gemma-4-e2b-it` |
| **المعلمات** | 2.3 مليار فعالة (5.1 مليار إجمالاً) |
| **سياق الإدخال** | 128,000 Token |
| **الوسائط** | نص، صور، وصوت (Native Audio) |
| **الحجم (4-bit)** | ~1.5GB VRAM |
| **الأداء** | مصمم للأجهزة الطرفية وأجهزة IoT |
| **🔗 HuggingFace** | [google/gemma-4-e2b-it](https://huggingface.co/google/gemma-4-e2b-it) |

```powershell
huggingface-cli download google/gemma-4-e2b-it
```

#### Gemma 4 E4B — المتوسط القوي

| المواصفة | القيمة |
|----------|--------|
| **المعرف** | `google/gemma-4-e4b-it` |
| **المعلمات** | 4.5 مليار فعالة (8 مليار إجمالاً) |
| **سياق الإدخال** | 128,000 Token |
| **الوسائط** | نص، صور، وصوت (Native Audio) |
| **الحجم (4-bit)** | ~3GB VRAM |
| **الأداء** | يتفوق على نماذج الـ 7B القديمة في المنطق البرمجي |
| **🔗 HuggingFace** | [google/gemma-4-e4b-it](https://huggingface.co/google/gemma-4-e4b-it) |

```powershell
huggingface-cli download google/gemma-4-e4b-it
```

---

### 2️⃣ عائلة خليط الخبراء — MoE Family

معمارية هجينة فائقة الكفاءة — تفعّل فقط الخبراء المطلوبين.

#### Gemma 4 26B A4B (MoE) — السرعة مع الذكاء

| المواصفة | القيمة |
|----------|--------|
| **المعرف** | `google/gemma-4-26b-a4b-it` |
| **المعلمات** | 25.2 مليار إجمالي (3.8 مليار فعالة أثناء المعالجة) |
| **سياق الإدخال** | 256,000 Token |
| **الوسائط** | نص وصور (بدقة عالية) |
| **الحجم (4-bit)** | ~13.3GB VRAM |
| **الأداء** | فائق السرعة، مثالي للبرمجة المعقدة والوكلاء |
| **🔗 HuggingFace** | [google/gemma-4-26b-a4b-it](https://huggingface.co/google/gemma-4-26b-a4b-it) |

```powershell
huggingface-cli download google/gemma-4-26b-a4b-it
```

---

### 3️⃣ عائلة النماذج الكثيفة — Dense Frontier Family

النموذج الأضخم والأذكى في السلسلة.

#### Gemma 4 31B (Dense) — الوحش الحقيقي 🔥

| المواصفة | القيمة |
|----------|--------|
| **المعرف** | `google/gemma-4-31b-it` |
| **المعلمات** | 30.7 مليار معلمة (كثيف بالكامل) |
| **سياق الإدخال** | 256,000 Token |
| **الوسائط** | نص وصور (أعلى دقة في فهم المستندات) |
| **الحجم (4-bit)** | ~16.4GB VRAM |
| **الأداء** | المركز #3 عالمياً بين النماذج المفتوحة — تفكير منطقي عميق |
| **🔗 HuggingFace** | [google/gemma-4-31b-it](https://huggingface.co/google/gemma-4-31b-it) |

```powershell
huggingface-cli download google/gemma-4-31b-it
```

---

### 📊 جدول المقارنة الشامل

| النموذج | المعلمات | VRAM (4-bit) | السياق | الوسائط | الاستخدام الأمثل |
|---------|----------|-------------|--------|---------|-----------------|
| `gemma-4-e2b-it` | 2.3B | ~1.5GB | 128K | نص+صور+صوت | بحث سريع، تلخيص، مسودات |
| `gemma-4-e4b-it` | 4.5B | ~3GB | 128K | نص+صور+صوت | أكواد متوسطة، تحليل بيانات |
| `gemma-4-26b-a4b-it` | 25.2B (MoE) | ~13.3GB | 256K | نص+صور | برمجة معقدة، محاكاة منطقية |
| `gemma-4-31b-it` | 30.7B (Dense) | ~16.4GB | 256K | نص+صور | تفكير عميق، قرارات معقدة |

### ℹ️ معلومات تقنية هامة

- **المستودع الرسمي:** [google-deepmind/gemma](https://github.com/google-deepmind/gemma)
- **الترخيص:** Apache 2.0 (مفتوحة بالكامل)
- **تحديث المكتبات:**
  ```powershell
  pip install -U transformers huggingface_hub
  ```

---

## 🏛️ البنية المعمارية — Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    🖥️ Presentation Layer                    │
│    main_window.py │ customization_dialog.py │ components.py │
│    app_style.py │ details_dialog.py │ diagnosis_dialog.py   │
├─────────────────────────────────────────────────────────────┤
│                    🔄 Orchestration Layer                   │
│              ai_worker.py │ orchestrator.py                 │
├─────────────────────────────────────────────────────────────┤
│                    🧠 AI Engine Layer                       │
│                       ai_engine.py                          │
├─────────────────────────────────────────────────────────────┤
│                    💾 Data Layer                             │
│          database.py │ SQLite │ JSON Configs                │
└─────────────────────────────────────────────────────────────┘
```

### 📁 هيكل المشروع — Project Structure

```
Agentic-Swarm/
├── 📄 desktop_app.py          ← Entry point — نقطة الدخول
├── 📄 run_project.ps1         ← Auto-launch script — سكربت التشغيل التلقائي
├── 📄 fix_os_1455.ps1         ← Virtual memory fix — إصلاح الذاكرة الافتراضية
├── 📄 requirements.txt        ← Python dependencies — المكتبات المطلوبة
├── 📁 backend/
│   ├── 📄 ai_engine.py        ← AI model loader/generator — محرك الذكاء الاصطناعي
│   ├── 📄 orchestrator.py     ← Agent orchestration — المنسق المركزي
│   └── 📄 database.py         ← SQLite database — قاعدة البيانات
├── 📁 gui/
│   ├── 📄 main_window.py      ← Main window (3-panel layout) — النافذة الرئيسية
│   ├── 📄 customization_dialog.py ← Agent customization — تخصيص الوكلاء
│   ├── 📄 diagnosis_dialog.py ← Live diagnostics — التشخيص الحي
│   ├── 📄 details_dialog.py   ← Model details viewer — عارض التفاصيل
│   ├── 📄 components.py       ← Custom widgets — مكونات مخصصة
│   ├── 📄 app_style.py        ← WhatsApp Dark QSS — أنماط التصميم
│   ├── 📄 ai_worker.py        ← Background QThreads — خيوط العمل
│   └── 📄 models_data.py      ← Model specs HTML — بيانات النماذج
└── 📁 config/
    ├── 📄 current_config.json ← Active agent config — إعدادات الوكلاء
    └── 📄 settings.json       ← Global settings — الإعدادات العامة
```

---

## 💡 كيف يعمل؟ — How It Works

```
المستخدم يكتب فكرة → SwarmWorker (QThread) → Orchestrator → حلقة لا نهائية:
  │
  ├── الوكيل #1: تحميل النموذج → توليد (Streaming) → تفريغ VRAM
  ├── الوكيل #2: تحميل النموذج → توليد (Streaming) → تفريغ VRAM
  ├── الوكيل #3: تحميل النموذج → توليد (Streaming) → تفريغ VRAM
  ├── الوكيل #4: تحميل النموذج → توليد (Streaming) → تفريغ VRAM
  └── الوكيل #5: تحميل النموذج → توليد (Streaming) → تفريغ VRAM → حفظ المسودة
        │
        └── العودة للوكيل #1 (دورة جديدة) ← ∞
```

### استراتيجية إدارة الذاكرة — VRAM Management

| النموذج | الاستراتيجية |
|---------|-------------|
| E2B / E4B | GPU فقط — يتسع بسهولة |
| 26B MoE | GPU مع حد `max_memory: 14.5GiB` |
| 31B Dense | GPU 14.5GiB + CPU Offload 16GiB |

**التفريغ النووي بعد كل وكيل:**
```python
accelerate.release_memory(model) → del model → gc.collect() → torch.cuda.empty_cache() → torch.cuda.synchronize()
```

---

## 🎮 الاستخدام — Usage

### بدء جلسة عصف ذهني
1. شغّل البرنامج عبر `.\run_project.ps1`
2. اكتب فكرتك في مربع الإدخال
3. اضغط **Enter** — الوكلاء سيبدأون العمل تلقائياً

### تخصيص الوكلاء
- اضغط **🎛️ تخصيص النماذج والوكلاء**
- غيّر اسم كل وكيل ودوره والنموذج المستخدم
- أو اكتب وصفاً واضغط **"بدء تخصيص الكل"** للتخصيص بالذكاء الاصطناعي

### التدخل أثناء العمل
- اكتب رسالة جديدة أثناء عمل الوكلاء → ستُحقن كـ "أمر إداري"

---

## 🛠️ التقنيات المستخدمة — Tech Stack

| التقنية | الاستخدام |
|---------|-----------|
| [Python 3.13](https://www.python.org/) | اللغة الأساسية |
| [PySide6 (Qt 6)](https://doc.qt.io/qtforpython-6/) | واجهة سطح المكتب الأصلية |
| [PyTorch](https://pytorch.org/) | محرك الحساب التنسوري GPU |
| [Hugging Face Transformers](https://huggingface.co/docs/transformers) | تحميل وتشغيل النماذج |
| [BitsAndBytes](https://github.com/bitsandbytes-foundation/bitsandbytes) | ضغط 4-bit NF4 |
| [Accelerate](https://huggingface.co/docs/accelerate) | إدارة device_map و CPU offload |
| [SQLite3](https://www.sqlite.org/) | قاعدة البيانات المحلية |

---

## ❓ حل المشاكل الشائعة — Troubleshooting

<details>
<summary><b>❌ <code>python is not recognized</code></b></summary>

**السبب:** لم تُفعّل "Add to PATH" أثناء تثبيت Python.
**الحل:** أعد تثبيت Python وفعّل الخيار.
</details>

<details>
<summary><b>❌ <code>torch.cuda.is_available()</code> يرجع <code>False</code></b></summary>

**الحل:**
1. تأكد من تثبيت CUDA Toolkit
2. أعد تثبيت PyTorch: `pip install torch --index-url https://download.pytorch.org/whl/cu126`
3. أعد تشغيل الكمبيوتر
</details>

<details>
<summary><b>❌ <code>CUDA out of memory</code></b></summary>

**الحل:** غيّر النموذج المعيّن لكل وكيل إلى `gemma-4-e2b-it` (الأصغر) من نافذة التخصيص.
</details>

<details>
<summary><b>❌ <code>execution of scripts is disabled</code></b></summary>

```powershell
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
```
</details>

<details>
<summary><b>❌ <code>OSError: model not found</code></b></summary>

**السبب:** النموذج غير محمّل.
**الحل:** `huggingface-cli download google/gemma-4-e2b-it`
</details>

---

## 📄 الترخيص — License

This project is licensed under the **Apache License 2.0** — see the [LICENSE](LICENSE) file for details.

The Gemma-4 models are also licensed under [Apache 2.0](https://github.com/google-deepmind/gemma) by Google DeepMind.

---

## 🙏 شكر وتقدير — Acknowledgments

- [Google DeepMind](https://deepmind.google/) — لنماذج Gemma-4 المفتوحة
- [Hugging Face](https://huggingface.co/) — لاستضافة النماذج ومكتبة Transformers
- [The Qt Company](https://www.qt.io/) — لإطار عمل Qt 6 و PySide6
- [PyTorch](https://pytorch.org/) — لمحرك الحساب التنسوري

---

<p align="center">
  <sub>Built with ❤️ for the open-source AI community</sub>
</p>
