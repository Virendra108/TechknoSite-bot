import asyncio
from dataclasses import dataclass, field
from datetime import date
import logging
from pathlib import Path
from uuid import UUID, uuid4

from telegram import Message, Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

from config import load_settings
from services.db_service import DBService
from services.docx_service import DocxService
from services.extraction_service import ExtractionService
from services.stt_service import STTService


@dataclass
class ReportSession:
    job_id: UUID
    chat_id: int
    image_paths: list[Path] = field(default_factory=list)


sessions: dict[int, ReportSession] = {}
settings = load_settings()
stt_service = STTService(settings.groq_api_key, settings.groq_stt_model)
extraction_service = ExtractionService(settings.groq_api_key, settings.groq_llm_model)
docx_service = DocxService(settings.template_path, settings.output_dir)
db_service = DBService(settings)
logging.basicConfig(
    filename="bot.log",
    level=logging.WARNING,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)
logger = logging.getLogger(__name__)
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("telegram").setLevel(logging.WARNING)
logging.getLogger("telegram.ext").setLevel(logging.INFO)

SUPPORTED_AUDIO_EXTENSIONS = {
    ".ogg",
    ".oga",
    ".opus",
    ".mp3",
    ".mp4",
    ".mpeg",
    ".mpga",
    ".wav",
    ".m4a",
    ".aac",
    ".flac",
    ".webm",
}


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Hi. Send /newreport to start a daily progress report, then upload photos and finish with one voice note or audio file."
    )


async def new_report(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_chat.id
    job_id = uuid4()
    sessions[chat_id] = ReportSession(job_id=job_id, chat_id=chat_id)
    await update.message.reply_text(
        f"New report started. Job ID: {job_id}\n"
        "Send site photos first, then one voice note or audio file to generate the report."
    )


async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_chat.id
    session = sessions.get(chat_id)
    if not session:
        await update.message.reply_text("Please send /newreport before uploading photos.")
        return

    photo = update.message.photo[-1]
    file = await context.bot.get_file(photo.file_id)
    position = len(session.image_paths) + 1
    image_path = settings.download_dir / f"{session.job_id}_photo_{position}.jpg"
    await file.download_to_drive(custom_path=image_path)
    session.image_paths.append(image_path)

    if position > 4:
        await update.message.reply_text(
            f"Photo {position} saved. For this POC, only the first 4 photos will appear in the fixed report slots."
        )
    else:
        await update.message.reply_text(f"Photo {position} saved. Send more photos or send the voice note to finish.")


async def _process_audio_message(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    telegram_file_id: str,
    file_size: int | None,
    suffix: str,
    label: str,
) -> None:
    chat_id = update.effective_chat.id
    session = sessions.get(chat_id)
    if not session:
        await update.message.reply_text(f"Please send /newreport first, then photos and one {label}.")
        return

    size = file_size or 0
    if size > settings.audio_size_limit_bytes:
        size_mb = size / (1024 * 1024)
        await update.message.reply_text(
            f"Your audio is too large ({size_mb:.1f} MB). Please resend audio under "
            f"{settings.audio_size_limit_mb} MB."
        )
        return

    await update.message.reply_text(f"Processing {label} and building the report...")
    audio_path = settings.download_dir / f"{session.job_id}_audio{suffix}"

    try:
        file = await context.bot.get_file(telegram_file_id)
        await file.download_to_drive(custom_path=audio_path)

        transcript_en = await asyncio.to_thread(stt_service.translate_to_english, audio_path)
        report_data = await asyncio.to_thread(
            extraction_service.extract,
            transcript_en,
            str(session.job_id),
            date.today(),
        )
        report_path = await asyncio.to_thread(
            docx_service.render_report,
            str(session.job_id),
            report_data,
            session.image_paths,
        )
        await asyncio.to_thread(
            db_service.save_job,
            session.job_id,
            chat_id,
            transcript_en,
            session.image_paths,
        )

        with report_path.open("rb") as report_file:
            await update.message.reply_document(
                document=report_file,
                filename=report_path.name,
                caption="Daily progress report generated.",
        )
        sessions.pop(chat_id, None)
    except Exception:
        logger.exception("Processing failed for job %s", session.job_id)
        await update.message.reply_text(
            "Sorry, processing failed. Please try again, or resend the audio if the session is still open."
        )


async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    voice = update.message.voice
    await _process_audio_message(update, context, voice.file_id, voice.file_size, ".ogg", "voice note")


async def handle_audio(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    audio = update.message.audio
    suffix = Path(audio.file_name or "audio.mp3").suffix or ".mp3"
    await _process_audio_message(update, context, audio.file_id, audio.file_size, suffix, "audio file")


async def handle_audio_document(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    document = update.message.document
    suffix = Path(document.file_name or "audio").suffix or ".bin"
    mime_type = document.mime_type or ""
    if (
        suffix.lower() not in SUPPORTED_AUDIO_EXTENSIONS
        and not mime_type.startswith("audio/")
        and mime_type not in {"video/mp4", "video/webm"}
    ):
        await update.message.reply_text("I received a file, but it does not look like an audio file. Please send a voice note or audio file.")
        return
    await _process_audio_message(update, context, document.file_id, document.file_size, suffix, "audio file")


async def handle_video(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    video = update.message.video
    suffix = Path(video.file_name or "video.mp4").suffix or ".mp4"
    if suffix.lower() not in {".mp4", ".webm"}:
        await update.message.reply_text("Please send the audio as a voice note, MP3/M4A/WAV, or MP4 file.")
        return
    await _process_audio_message(update, context, video.file_id, video.file_size, suffix, "MP4 audio/video file")


async def handle_unknown_document(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    document = update.message.document
    suffix = Path(document.file_name or "file").suffix.lower()
    mime_type = document.mime_type or ""
    if suffix in SUPPORTED_AUDIO_EXTENSIONS or mime_type.startswith("audio/") or mime_type in {"video/mp4", "video/webm"}:
        await handle_audio_document(update, context)
        return
    await update.message.reply_text("File received, but this POC only uses photos plus one voice note/audio file.")


async def handle_unknown_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Send /newreport, then photos, then one voice note or audio file.")


async def handle_error(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.exception("Unhandled bot error", exc_info=context.error)


def main() -> None:
    application = Application.builder().token(settings.telegram_bot_token).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("newreport", new_report))
    application.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    application.add_handler(MessageHandler(filters.VOICE, handle_voice))
    application.add_handler(MessageHandler(filters.AUDIO, handle_audio))
    application.add_handler(MessageHandler(filters.VIDEO, handle_video))
    application.add_handler(MessageHandler(filters.Document.AUDIO, handle_audio_document))
    application.add_handler(MessageHandler(filters.Document.ALL, handle_unknown_document))
    application.add_handler(MessageHandler(filters.ALL, handle_unknown_message))
    application.add_error_handler(handle_error)
    application.run_polling()


if __name__ == "__main__":
    main()
