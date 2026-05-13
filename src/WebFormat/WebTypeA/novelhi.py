import os
from dotenv import load_dotenv
from typing import Unpack
from src.WebFormat.models import IBase
from src.utils import clean_paragraph, decode_rot18
from .Base import WebTypeA


class Novelhi(WebTypeA):
    def __init__(self, **kwargs: Unpack[IBase]):
        """
        required args:
            - link: str
            - author: str
            - page: Page
            - (optional) start: int = 0
            - (optional) end: int
        """
        kwargs["source"] = "novelhi"
        super().__init__(**kwargs)

        load_dotenv()
        self._title_ref = os.getenv("NOVELHI_TITLE_DIV", None)
        self._chapter_index_ref = os.getenv("NOVELHI_CHAPTER_INDEX", None)
        self._content_ref = os.getenv("NOVELHI_CONTENT_ID", None)
        self._book_cover_ref = os.getenv("NOVELHI_COVER_IMG", None)
        self._set_chapter_tab_ref(os.getenv("NOVELHI_CHAPTER_TAB_ID", None))

    def _get_paragraph(self, text: str):
        return clean_paragraph(decode_rot18(text))
