from pathlib import Path
from typing import Any, Callable, Literal
from pypub import (  # type: ignore[import]
    Chapter,
    Epub,
    create_chapter_from_file,
    create_chapter_from_html,
    create_chapter_from_text,
    create_chapter_from_url,
)
from pathlib import Path
from tqdm import tqdm
from src.models import EBOOKCONTEXT, UNKNOWN
from src.WebFormat.models import IChapterInfo
from src.utils import file_to_dataclass, normalize_text


class EpubContext:
    """
    - file_path: Book docs folder path
    - (optional) title
    - (optional) creator
    - (optional) cover
    - (optional) publisher
    """

    def __init__(
        self,
        file_path: Path | str,
        chapter_index: list[IChapterInfo] | Path | None = None,
        title: str | None = None,
        creator: str | None = None,
        cover: Path | None = None,
        publisher: str | None = None,
    ):
        self.__file_path = Path(file_path)
        self.__title: str | None = title
        self.__creator: str | None = creator
        self.__publisher: str | None = publisher
        self.__cover: Path | None = cover
        self.__chapter_index: list[IChapterInfo] = []

        self.__set_book_info_from_index(chapter_index)
        self.__set_book_cover_path()

        self.__book_ctx = Epub(
            title=self.__title or UNKNOWN,
            creator=self.__creator or UNKNOWN,
            publisher=self.__publisher or UNKNOWN,
            cover=str(self.__cover),
        )

    def __set_book_info_from_index(
        self, chapter_index: list[IChapterInfo] | Path | None
    ):
        if not chapter_index:
            chapter_index = self.__file_path / EBOOKCONTEXT.INDEX_FILE_NAME

        if isinstance(chapter_index, Path):
            if (
                len(
                    value := file_to_dataclass(
                        chapter_index, lambda x: IChapterInfo(**x)
                    )
                )
                < 1
            ):
                raise ValueError(
                    f"No data found in {EBOOKCONTEXT.INDEX_FILE_NAME} file."
                )

            self.__chapter_index = value
        else:
            self.__chapter_index = chapter_index

        self.__title = self.__title or self.__chapter_index[0].title
        self.__creator = self.__creator or self.__chapter_index[0].author
        self.__publisher = self.__publisher or self.__chapter_index[0].page_name

    def __set_book_cover_path(self):
        if not self.__cover:
            self.__cover = self.__file_path / EBOOKCONTEXT.COVER_FILE_NAME

        if not self.__cover.exists():
            self.__cover = None

    def __add_chapter(
        self,
        title: str,
        content: str | Path,
        source_type: Literal["file", "html", "text", "url"] = "text",
    ):
        """
        - "file" - allow .html / .xhtml files only.
        - "html" - Create a chapter from string or HTML string.
        - "text" - Create a chapter from plain text (no HTML allowed).
        - "url" - Convert webpage into a EPUB page.
        """
        chapter_creators: dict[str, Callable[[Any, str], Chapter]] = {
            "file": lambda x, y: create_chapter_from_file(x, y),
            "html": lambda x, y: create_chapter_from_html(x, y),
            "text": lambda x, y: create_chapter_from_text(x, y),
            "url": lambda x, y: create_chapter_from_url(x, y),
        }

        chapter = chapter_creators[source_type](content, title)
        self.__book_ctx.add_chapter(chapter)

    def create_ebook(self):

        with tqdm(
            iterable=self.__chapter_index,
            total=len(self.__chapter_index),
            desc="Inserting chapters",
            unit="chapter",
        ) as tbar:
            # add chapters to ebook
            for idx in tbar:
                if not idx.file_path:
                    continue
                content = Path(idx.file_path).read_text(encoding="utf-8")
                self.__add_chapter(idx.chapter_title, content)
            tbar.set_description("Insert chapters done.")

        counter = 1
        file_name = normalize_text(self.__title)
        save_to = self.__file_path / f"{file_name}.epub"
        while save_to.is_file():
            save_to = self.__file_path / f"{file_name} ({counter}).epub"
            counter += 1

        self.__book_ctx.create(str(save_to))
