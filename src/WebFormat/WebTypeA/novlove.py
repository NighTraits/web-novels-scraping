import os
from dotenv import load_dotenv
from typing import Unpack
from src.WebFormat.models import IBase
from .Base import WebTypeA


class NovLove(WebTypeA):
    def __init__(self, **kwargs: Unpack[IBase]):
        """
        Key Word Arguments:
            - link: str
            - author: str
            - page: Page
            - (optional) start: int = 0
            - (optional) end: int
        """
        kwargs["source"] = "novelov"
        super().__init__(**kwargs)

        load_dotenv()
        self._title_ref = os.getenv("NOVLOVE_TITLE_DIV", None)
        self._chapter_index_ref = os.getenv("NOVLOVE_CHAPTER_INDEX", None)
        self._content_ref = os.getenv("NOVLOVE_CONTENT_ID", None)
        self._book_cover_ref = os.getenv("NOVLOVE_COVER_IMG", None)
        self._set_chapter_tab_ref(os.getenv("NOVLOVE_CHAPTER_TAB_ID", None))
