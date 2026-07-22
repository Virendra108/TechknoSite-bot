from dataclasses import dataclass
import os
from pathlib import Path

from dotenv import load_dotenv


@dataclass(frozen=True)
class Settings:
    telegram_bot_token: str
    groq_api_key: str
    db_host: str
    db_port: int
    db_name: str
    db_user: str
    db_password: str
    audio_size_limit_mb: int
    groq_stt_model: str
    groq_llm_model: str
    template_path: Path
    output_dir: Path
    download_dir: Path

    @property
    def audio_size_limit_bytes(self) -> int:
        return self.audio_size_limit_mb * 1024 * 1024


def _required(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


def load_settings() -> Settings:
    load_dotenv()
    settings = Settings(
        telegram_bot_token=_required("TELEGRAM_BOT_TOKEN"),
        groq_api_key=_required("GROQ_API_KEY"),
        db_host=os.getenv("DB_HOST", "localhost"),
        db_port=int(os.getenv("DB_PORT", "5432")),
        db_name=_required("DB_NAME"),
        db_user=_required("DB_USER"),
        db_password=_required("DB_PASSWORD"),
        audio_size_limit_mb=int(os.getenv("AUDIO_SIZE_LIMIT_MB", "24")),
        groq_stt_model=os.getenv("GROQ_STT_MODEL", "whisper-large-v3"),
        groq_llm_model=os.getenv("GROQ_LLM_MODEL", "llama-3.3-70b-versatile"),
        template_path=Path(os.getenv("TEMPLATE_PATH", "templates/report_template.docx")),
        output_dir=Path(os.getenv("OUTPUT_DIR", "outputs")),
        download_dir=Path(os.getenv("DOWNLOAD_DIR", "downloads")),
    )
    settings.output_dir.mkdir(parents=True, exist_ok=True)
    settings.download_dir.mkdir(parents=True, exist_ok=True)
    return settings
