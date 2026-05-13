
from dataclasses import dataclass, field
from enum import StrEnum
from pathlib import Path
from typing import Literal

from playwright.async_api import Page

class ELOADSTATE(StrEnum):
    DOMCONTENTLOADED = 'domcontentloaded'
    LOAD = 'load'
    NETWORKIDLE = 'networkidle'

@dataclass
class IBase:
    link: str
    author: str
    source: str

class INovelhi(IBase):
    start: int | None = field(default=0)
    end: int | None = field(default=None)

@dataclass
class IChapterInfo:
    title:str
    chapter: int
    link:str
    file_path:Path | None

    def update(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

@dataclass
class ILinkInfo:
    href: str | None
    text: str