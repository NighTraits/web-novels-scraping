from enum import StrEnum

UNKNOWN = "Unknown"


class EBOOKCONTEXT(StrEnum):
    COVER_FILE_NAME = "book-cover.png"
    INDEX_FILE_NAME = "book-index.json"
    CHAPTER_FOLDER_NAME = "chapters"
