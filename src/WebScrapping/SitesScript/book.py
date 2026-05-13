import json
from pathlib import Path
from typing import Unpack
from src.utils import dataclass_to_dict
from WebScrapping.models import IChapterInfo, IBase

class BookContext:
    def __init__(self, **kwargs: Unpack[IBase]):
        self.__link = kwargs["link"]
        self.__author = kwargs["author"]
        self.__source = kwargs["source"]
        self.__title: str | None = None
        
        self.__cover_path: Path | None = None

        self._temp_path = Path('temp')
        self._files_path: Path | None = None
        self._chapter_path: Path | None = None
        self._index_file: Path | None = None

    @property
    def link(self):
        return self.__link
    
    @property
    def author(self):
        return self.__author
    
    @property
    def title(self):
        return self.__title
    
    @property
    def cover(self):
        return self.__cover_path
    
    @property
    def get_chapters_location(self):
        return self._chapter_path
    
    def set_cover(self, file_name):
        self.__cover_path = self._files_path / file_name
    
    def set_title(self, title: str):
        self.__title = title

    def set_title_and_create_directory(self, title: str):
        self.set_title(title)
        self.__create_file_folder(title)
    
    # private method
    def __create_file_folder(self, folder_name: str):

        self._files_path = self._temp_path / f"{folder_name} ({self.__source})"
        self._chapter_path = self._files_path / "chapters"
        
        # create dir all the way to chapter folder
        self._chapter_path.mkdir(parents=True, exist_ok=True)
    
    def save_index_file(self, data: list[IChapterInfo]) -> bool:
        try:
            self._index_file = self._files_path / "index.json"
            index_json = dataclass_to_dict(data)

            self._index_file.write_text(json.dumps(index_json, indent=2))

            return True
        
        except:
            print("An error ocurred while attempting to save the chapters index as a json file.")
            return False
        
    def to_epub(self, index_path: Path | None = None):
        if not self._index_file and not index_path:
            print("Required directory to the index.json file not found.")
            return False
        
        # read index file
        with open(self._index_file, 'r+') as file:
            data = file.read()
