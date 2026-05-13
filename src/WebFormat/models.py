from dataclasses import dataclass, field
from pathlib import Path
from typing import NotRequired, TypedDict


class IHtmlRef(TypedDict):
    title_re: str
    index_ta: str
    index_re: str
    content_re: str
    book_cover_re: str


class IBase(TypedDict):
    link: str
    author: NotRequired[str | None]
    source: NotRequired[str | None]
    start: NotRequired[int | None]
    end: NotRequired[int | None]


@dataclass
class IChapterInfo:
    title: str
    author: str
    page_name: str
    chapter_link: str | None
    chapter_title: str
    chapter_number: int
    file_path: Path | None = field(default=None)
