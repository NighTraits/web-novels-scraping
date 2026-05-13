from dataclasses import dataclass
from pathlib import Path
from typing import Literal
import pypub
from pypub import Epub, epub
from pathlib import Path

from WebScrapping.models import IChapterInfo

class EpubContext:
    def __init__(self, title = '', creator = '', cover = None, publisher = None, file_path: Path = None):  
        if file_path.exists():
            file_path.unlink()

        self._book = Epub(
            title=title, 
            creator=creator, 
            publisher=publisher, 
            cover=cover,
        )

        self.file_path = file_path
    
    def add_chapter(self, 
        title: str, 
        content: str | Path, 
        source_type: Literal['file', 'html', 'text', 'url'] = 'text'
    ):
        """
            "file" - allow .html / .xhtml files only. \n
            "html" - Create a chapter from string or HTML string. \n
            "text" - Create a chapter from plain text (no HTML allowed). \n
            "url" - Convert webpage into a EPUB page.
        """
        chapter_creators = {
            "file": lambda x, y: pypub.create_chapter_from_file(x, y),
            "html": lambda x, y: pypub.create_chapter_from_html(x, y),
            "text": lambda x, y: pypub.create_chapter_from_text(x, y),
            "url":  lambda x, y: pypub.create_chapter_from_url(x, y),
        }

        chapter = chapter_creators[source_type](content, title)
        self._book.add_chapter(chapter)

    def create_book(self):
        self._book.create(str(self.file_path))

    def files_to_epub(self, files: list[IChapterInfo]):
        
        for file in files:
            if not file.file_path:
                continue
            content = Path(file.file_path).read_text()
            self.add_chapter(file.title, content)

        self.create_book()
