from dataclasses import asdict
import json
from pathlib import Path
import codecs
import re
from typing import Any, Callable, TypeVar

from src.models import UNKNOWN

T = TypeVar("T")


def _create_directory(file_path: Path) -> Path:
    if file_path.suffix:
        file_path = file_path.parent
    file_path.mkdir(parents=True, exist_ok=True)
    return file_path


def save_as(file_path: Path, file_content: str) -> Path:
    _create_directory(file_path)
    file_path.write_text(file_content, encoding="utf-8")
    return file_path


def decode_rot18(text: str) -> str:
    rot_5_table = str.maketrans("0123456789", "5678901234")
    rot_13_text = codecs.decode(text, "rot_13")
    return rot_13_text.translate(rot_5_table)


def dataclass_to_dict(data: list[Any]) -> list[dict[str, Any]]:
    dict_data = [asdict(dt) for dt in data]
    dict_data = [
        {
            key: str(value) if isinstance(value, Path) else value
            for key, value in data.items()
        }
        for data in dict_data
    ]
    return dict_data


def file_to_dataclass(
    file_path: Path, convert: Callable[[dict[str, Any]], T]
) -> list[T]:
    if Path(file_path).stat().st_size == 0:
        return []
    with open(file_path, "r", encoding="utf-8") as file:
        data = json.load(file)
    return [convert(d) for d in data]


def clean_paragraph(text: str) -> str:
    return re.sub(r"\n+0\n+|\n+", "\n", text)


def normalize_text(text: str | None) -> str:
    if not text:
        return ""
    return re.sub(r'[\\/*?:"<>|]', "", text.strip())


def get_site_from_link(link: str) -> str:
    match = re.search(r"\/{2}(.*)\.", link)
    if match:
        return match.group(1)
    return UNKNOWN


def natural_sort_key(path: Path) -> tuple[str, ...]:
    """Split string into text/number chunks so '2' < '10' numerically."""
    name: str = path.name
    chunks: list[str] = re.split(r"(\d+)", name)
    return tuple(
        chunk.zfill(10) if chunk.isdigit() else chunk.lower() for chunk in chunks
    )
