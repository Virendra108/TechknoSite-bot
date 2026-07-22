````markdown
# 📋 Telegram Daily Progress Report Bot

> An AI-powered Telegram bot that converts voice notes into structured daily project progress reports and automatically generates a professional Microsoft Word (`.docx`) document.

Designed as a local **Proof of Concept (POC)**, this project demonstrates an end-to-end AI pipeline integrating speech transcription, LLM-based information extraction, dynamic document generation, and PostgreSQL persistence.

---

## ✨ Features

- 📷 **Multi-Format Media Support**
  - Accepts Telegram photos, voice notes, audio files, and `.mp4` video messages.

- 🎙️ **Intelligent Audio Processing**
  - Validates uploaded media before downloading.
  - Enforces a configurable **24 MB** file size limit to optimize API usage.

- 🌐 **Speech Transcription & Translation**
  - Uses **Groq Whisper (`whisper-large-v3`)** to transcribe speech.
  - Automatically translates Hindi, Marathi, and Hinglish into English.

- 🤖 **AI-Powered Information Extraction**
  - Uses **Llama 3.3 70B Versatile** with strict JSON schema validation.
  - Extracts:
    - Work summary
    - Completed tasks
    - Issues encountered
    - Resource requirements
    - Next-day work plan
  - Prevents fabrication of missing information.

- 📄 **Dynamic Word Report Generation**
  - Generates a professional Microsoft Word (`.docx`) report.
  - Automatically populates multiple tables.
  - Removes unused repeating sections.
  - Inserts only the uploaded site photographs while preserving document formatting.

- 🗄️ **PostgreSQL Persistence**
  - Stores:
    - Generated Report ID
    - English transcript
    - Uploaded site photographs
  - Maintains a lightweight audit trail.

---

## 🛠️ Tech Stack

| Category | Technology |
|-----------|------------|
| Language | Python 3.11+ |
| Bot Framework | python-telegram-bot (v20+, Async) |
| Speech-to-Text | Groq Whisper (`whisper-large-v3`) |
| LLM | Groq Llama 3.3 70B Versatile |
| Document Generation | docxtpl |
| Database | PostgreSQL |
| Database Driver | psycopg2 |
| Environment Variables | python-dotenv |

---

## ⚙️ Prerequisites

Before running the project, ensure you have:

- Python **3.11+**
- PostgreSQL **15+**
- Telegram Bot Token (from **@BotFather**)
- Groq API Key

---

# 📦 Installation

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/telegram-progress-bot.git

cd telegram-progress-bot
```

---

### 2. Create a Virtual Environment

#### Windows

```bash
python -m venv .venv

.\.venv\Scripts\activate
```

#### Linux / macOS

```bash
python -m venv .venv

source .venv/bin/activate
```

---

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

### 4. Configure Environment Variables

Copy the example configuration file.

```bash
cp .env.example .env
```

Update the `.env` file.

```env
TELEGRAM_BOT_TOKEN=your_telegram_token

GROQ_API_KEY=your_groq_api_key

DB_HOST=localhost
DB_PORT=5433
DB_NAME=techknosite_reports
DB_USER=techknosite_bot
DB_PASSWORD=your_db_password

AUDIO_SIZE_LIMIT_MB=24
```

---

### 5. Initialize PostgreSQL

If you're using the provided helper scripts (Windows):

```powershell
PowerShell -ExecutionPolicy Bypass -File .\db\setup_poc_postgres.ps1

PowerShell -ExecutionPolicy Bypass -File .\db\start_poc_postgres.ps1
```

Create the database schema.

```bash
python db/init_db.py
```

---

# 🚀 Running the Bot

Start the bot.

```bash
python start_bot.py
```

To stop it gracefully:

```bash
python stop_bot.py
```

---

# 📱 Usage

1. Start the bot.

```
/start
```

2. Create a new report session.

```
/newreport
```

3. Upload one or more site photographs.

4. Upload a voice note, audio file, or `.mp4` describing the day's work.

5. Wait a few seconds while the AI processes your report.

6. Receive a fully generated Microsoft Word (`.docx`) report containing:
   - Work summary
   - Completed tasks
   - Issues encountered
   - Resource requirements
   - Next-day work plan
   - Uploaded site photographs

---

# 🗄️ Database Schema

The application uses a lightweight persistence layer.

## `report_jobs`

Stores:

- Report UUID
- Telegram Chat ID
- Report metadata

---

## `report_audio_text`

Stores:

- English transcript returned by Groq Whisper

---

## `report_images`

Stores:

- Uploaded photographs
- Binary image data (`BYTEA`)
- Image ordering index

---

# 🔄 Application Workflow

```text
Telegram User
      │
      ▼
Upload Photos
      │
      ▼
Upload Voice Note / Audio / MP4
      │
      ▼
Telegram Bot
      │
      ▼
Groq Whisper
(Speech → English Transcript)
      │
      ▼
Llama 3.3 70B
(Structured JSON Extraction)
      │
      ▼
PostgreSQL Storage
      │
      ▼
docxtpl
(Generate Word Report)
      │
      ▼
Telegram
(Return Generated .docx)
```

---

# 📂 Project Structure

```text
telegram-progress-bot/
│
├── bot/
├── handlers/
├── services/
├── database/
├── templates/
├── db/
├── start_bot.py
├── stop_bot.py
├── requirements.txt
├── .env.example
└── README.md
```

---

# 🎯 Proof of Concept Scope

This project demonstrates:

- Telegram Bot Development
- Speech-to-Text using AI
- Multilingual Translation
- LLM-based Information Extraction
- Dynamic Microsoft Word Report Generation
- PostgreSQL Integration
- End-to-End AI Automation Workflow

---

# 🚀 Future Improvements

- [ ] Docker support
- [ ] Cloud deployment
- [ ] Report history
- [ ] Multi-user authentication
- [ ] OCR from uploaded images
- [ ] PDF report generation
- [ ] Admin dashboard
- [ ] Email report delivery

---

# 👨‍💻 Author

**Virendra Ghule**

---
````
