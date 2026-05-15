from src.EpubFile import EpubContext
from src.Sites.blogspot import Blogspot
from src.WebFormat.enums import BaseRef
from src.models import UNKNOWN


async def get_from_blogspot(
    ref: BaseRef,
    link: str,
    start: int,
    end: int,
    author: str = UNKNOWN,
    title: str | None = None,
):
    index_file = await Blogspot(
        ref=ref,
        link=link,
        author=author,
        title=title,
        start=start,
        end=end,
    ).create()
    EpubContext(file_path=index_file).create_ebook()
