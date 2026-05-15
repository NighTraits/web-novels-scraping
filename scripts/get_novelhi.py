from src.EpubFile import EpubContext
from src.Sites import NovelHi
from src.WebFormat.enums import NOVELHI
from src.models import UNKNOWN


async def get_from_novelhi(
    link: str, author: str = UNKNOWN, start: int | None = None, end: int | None = None
):
    index_file = await NovelHi(
        ref=NOVELHI, link=link, author=author, start=start, end=end
    ).create()
    EpubContext(file_path=index_file).create_ebook()
