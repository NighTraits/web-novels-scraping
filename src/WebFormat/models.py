from dataclasses import dataclass, field
from pathlib import Path
from typing import NotRequired, TypedDict
from src.WebFormat.enums import EOrder


class IHtmlRef(TypedDict):
    title_re: str
    index_ta: str
    index_re: str
    content_re: str
    book_cover_re: str


class IBase(TypedDict):
    link: str
    title: NotRequired[str | None]
    author: NotRequired[str | None]
    source: NotRequired[str | None]
    start: NotRequired[int | None]
    end: NotRequired[int | None]
    order: NotRequired[EOrder | None]


@dataclass
class IChapterInfo:
    title: str
    author: str
    page_name: str
    chapter_link: str | None
    chapter_title: str
    chapter_number: str
    file_path: Path | None = field(default=None)
