from pathlib import Path
from uuid import UUID

import psycopg2
from psycopg2.extensions import connection

from config import Settings


class DBService:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def connect(self) -> connection:
        return psycopg2.connect(
            host=self.settings.db_host,
            port=self.settings.db_port,
            dbname=self.settings.db_name,
            user=self.settings.db_user,
            password=self.settings.db_password,
        )

    def init_schema(self, schema_path: Path = Path("db/schema.sql")) -> None:
        with self.connect() as conn, conn.cursor() as cur:
            cur.execute(schema_path.read_text(encoding="utf-8"))

    def save_job(self, job_id: UUID, chat_id: int, transcript_en: str, image_paths: list[Path]) -> None:
        with self.connect() as conn, conn.cursor() as cur:
            cur.execute(
                "INSERT INTO report_jobs (job_id, chat_id) VALUES (%s, %s)",
                (str(job_id), chat_id),
            )
            cur.execute(
                "INSERT INTO report_audio_text (job_id, transcript_en) VALUES (%s, %s)",
                (str(job_id), transcript_en),
            )
            for position, image_path in enumerate(image_paths, start=1):
                cur.execute(
                    "INSERT INTO report_images (job_id, image_data, position) VALUES (%s, %s, %s)",
                    (str(job_id), psycopg2.Binary(image_path.read_bytes()), position),
                )
