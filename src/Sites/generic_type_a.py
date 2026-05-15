from typing import Unpack
from src.WebFormat.enums import BaseRef
from src.WebFormat.models import IBase
from src.WebFormat import WebTypeA
from src.models import UNKNOWN
from src.utils import get_site_from_link


class GenericTypeA(WebTypeA):
    def __init__(self, ref: BaseRef, **kwargs: Unpack[IBase]):
        """
        Key Word Arguments:
            - link: str
            - author: str
            - page: Page
            - (optional) start: int = 0
            - (optional) end: int
        """
        kwargs["source"] = get_site_from_link(kwargs["link"]) or UNKNOWN
        super().__init__(ref, **kwargs)
