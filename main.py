import asyncio
from scripts import get_from_novelhi, get_from_novlove
from src.EpubFile.epub_context import EpubContext


async def main():
    await asyncio.gather(
        get_from_novelhi(
            link="link",
            # author="author",  # optional
        ),
        get_from_novlove(
            link="link",
            # author="author",  # optional
        ),
    )


if __name__ == "__main__":

    asyncio.run(main())

    # create the book
    EpubContext(file_path="temp/book-name").create_ebook()
