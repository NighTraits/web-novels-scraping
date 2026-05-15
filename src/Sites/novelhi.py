from typing import Unpack
from src.WebFormat.enums import BaseRef
from src.WebFormat.models import IBase
from src.utils import clean_paragraph, decode_rot18
from src.WebFormat import WebTypeA


class NovelHi(WebTypeA):
    def __init__(self, ref: BaseRef, **kwargs: Unpack[IBase]):
        """
        required args:
            - link: str
            - author: str
            - page: Page
            - (optional) start: int = 0
            - (optional) end: int
        """
        kwargs["source"] = "novelhi"
        super().__init__(ref, **kwargs)

    def _get_paragraph(self, text: str):
        return clean_paragraph(decode_rot18(text))
