from src.EpubFile import EpubContext
from src.WebFormat import NovLove
from src.models import UNKNOWN


async def get_from_novlove(
    link: str, author: str = UNKNOWN, start: int | None = None, end: int | None = None
):
    index_file = await NovLove(
        link=link,
        author=author,
        start=start,
        end=end,
    ).create()
    EpubContext(file_path=index_file).create_ebook()
