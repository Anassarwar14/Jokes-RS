"""Load joke text metadata from the raw dataset."""
from pathlib import Path
import re
from typing import Dict

PROJECT_ROOT = Path(__file__).resolve().parents[2]
JOKES_DIR = PROJECT_ROOT / "data" / "raw" / "jokes_text" / "jokes"


def _extract_joke_text(html: str) -> str:
    text = re.sub(r"<!--begin of joke -->", "", html, flags=re.I)
    text = re.sub(r"<!--end of joke -->", "", text, flags=re.I)
    text = re.sub(r"<[^>]+>", "", text)
    text = text.replace("\r", " ").replace("\n", " ")
    text = re.sub(r"\s+", " ", text).strip()
    return text


class JokeCatalog:
    """Provides joke text lookup for joke IDs."""

    _jokes: list[str] | None = None

    @classmethod
    def load_jokes(cls) -> list[str]:
        if cls._jokes is not None:
            return cls._jokes

        if not JOKES_DIR.exists():
            raise FileNotFoundError(f"Jokes directory not found: {JOKES_DIR}")

        joke_texts = []
        html_files = sorted(
            JOKES_DIR.glob("init*.html"),
            key=lambda path: int(re.search(r"init(\d+)\.html", path.name).group(1)),
        )

        for html_file in html_files:
            html = html_file.read_text(errors="ignore")
            jokes = re.findall(r"<!--begin of joke -->(.*?)<!--end of joke -->", html, flags=re.S | re.I)
            if not jokes:
                jokes = [html]
            for joke in jokes:
                joke_texts.append(_extract_joke_text(joke))

        cls._jokes = joke_texts
        return cls._jokes

    @classmethod
    def get_joke_text(cls, joke_id: int) -> str | None:
        jokes = cls.load_jokes()
        if 0 <= joke_id < len(jokes):
            return jokes[joke_id]
        return None

    @classmethod
    def list_jokes(cls, limit: int | None = None) -> list[dict[str, object]]:
        jokes = cls.load_jokes()
        if limit is not None:
            jokes = jokes[:limit]
        return [{"joke_id": idx, "joke_text": text} for idx, text in enumerate(jokes)]
