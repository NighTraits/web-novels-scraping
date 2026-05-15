from src.EpubFile import EpubContext
from src.Sites.wordpress_a import Wordpress
from src.WebFormat.enums import BaseRef
from src.models import UNKNOWN


async def get_from_wordpress(
    ref: BaseRef,
    link: str,
    author: str = UNKNOWN,
    title: str | None = None,
    start: int | None = None,
    end: int | None = None,
):
    index_file = await Wordpress(
        ref=ref,
        link=link,
        author=author,
        title=title,
        start=start,
        end=end,
    ).create()
    EpubContext(file_path=index_file).create_ebook()
