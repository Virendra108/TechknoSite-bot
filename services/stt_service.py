from pathlib import Path

from groq import Groq


class STTService:
    def __init__(self, api_key: str, model: str) -> None:
        self.client = Groq(api_key=api_key)
        self.model = model

    def translate_to_english(self, audio_path: Path) -> str:
        with audio_path.open("rb") as audio_file:
            result = self.client.audio.translations.create(
                file=(audio_path.name, audio_file.read()),
                model=self.model,
                response_format="json",
            )
        return (getattr(result, "text", None) or "").strip()
