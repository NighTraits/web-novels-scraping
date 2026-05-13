from dataclasses import dataclass
import dataclasses
from pathlib import Path
import codecs
import re

def save_as(file_name: str, file_path: Path, file_content: str) -> str:
    file_path: Path = file_path / file_name
    file_path.write_text(file_content, encoding="utf-8")
    # relative_path = file_path.relative_to(Path.cwd())
    return str(file_path)


def decode_rot18(text: str) -> str:
    rot_5_table = str.maketrans("0123456789", "5678901234")
    rot_13_text = codecs.decode(text, 'rot_13')
    return rot_13_text.translate(rot_5_table)


def dataclass_to_dict(data: list[dataclass]):
    return [dataclasses.asdict(dt) for dt in data]


def clean_paragraph(text: str) -> str:
    return re.sub(r'\n+0\n+|\n{3,}', '\n\n', text)