import json
from pathlib import Path
from typing import Unpack
from src.models import EBOOKCONTEXT, UNKNOWN
from src.WebFormat.models import EOrder, IBase, IChapterInfo
from src.utils import dataclass_to_dict, get_site_from_link, file_to_dataclass


class BookContext:
    def __init__(self, **kwargs: Unpack[IBase]):
        self.__link: str = kwargs["link"]
        self.__author: str = kwargs.get("author") or UNKNOWN
        self.__source: str = kwargs.get("source") or get_site_from_link(self.__link)
        self.__title: str = UNKNOWN

        self._book_cover_path: Path
        self._book_index_path: Path
        self._chapter_order: EOrder = kwargs.get("order") or EOrder.ASC

        self._temp_path = Path("temp")
        self._files_path: Path
        self._chapter_path: Path

        self._chap_info: list[IChapterInfo] = []

        if title := kwargs.get("title"):
            self.__title = title
            self.set_title_and_create_directory(self.title)

        self.__set_page_range(kwargs.get("start"), kwargs.get("end"))

    @property
    def link(self) -> str:
        return self.__link

    @property
    def author(self) -> str:
        return self.__author or UNKNOWN

    @property
    def title(self) -> str:
        return self.__title or UNKNOWN

    @property
    def cover(self) -> Path:
        return self._book_cover_path

    @property
    def chapters(self) -> Path:
        return self._chapter_path

    @property
    def source(self) -> str:
        return self.__source or UNKNOWN

    def __set_page_range(self, start: int | None, end: int | None):
        self._start = 0
        self._end = None
        if not any([start, end]):
            return

        if (start and start < 1) or (end and end < 1):
            raise ValueError("Invalid chapters range.")

        if start:
            self._start = start - 1

        if end:
            self._end = end

    def set_title_and_create_directory(self, title: str):
        self.set_title(title)
        self.__create_file_folder(title)

    def set_title(self, title: str):
        self.__title = title

    # def set_page_range(self, start: int, end: int):
    #     if start < 0 or end < 0:
    #         self._start = 0
    #         self._end = -1

    def __create_file_folder(self, folder_name: str):
        self._files_path = self._temp_path / f"{folder_name}"
        # create dir all the way to chapter folder
        (self._files_path / EBOOKCONTEXT.CHAPTER_FOLDER_NAME).mkdir(
            parents=True, exist_ok=True
        )
        self._chapter_path = Path(EBOOKCONTEXT.CHAPTER_FOLDER_NAME)

        # prepare book cover path
        self._book_cover_path = self._files_path / EBOOKCONTEXT.COVER_FILE_NAME

        # prepare book cover path
        self._book_index_path = self._files_path / EBOOKCONTEXT.INDEX_FILE_NAME

        self.__get_index_file()

    def __get_index_file(self):
        if not self._book_index_path.exists():
            self._book_index_path.touch(exist_ok=True)
            self._chap_info = []
            return
        self._chap_info = file_to_dataclass(
            self._book_index_path, lambda x: IChapterInfo(**x)
        )

    def save_index_file(self, data: list[IChapterInfo]) -> bool:
        try:
            index_json = dataclass_to_dict(data)
            self._book_index_path.write_text(
                json.dumps(index_json, indent=2, ensure_ascii=False), encoding="utf-8"
            )

            return True

        except:
            print(
                "An error ocurred while attempting to save the chapters index as a json file."
            )
            return False
