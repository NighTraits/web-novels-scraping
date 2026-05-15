from pathlib import Path
import re
from typing import NotRequired, TypedDict, Unpack

from tqdm import tqdm
from src.WebFormat.enums import BaseRef
from src.WebFormat.models import IChapterInfo
from src.WebScrapping.Camoufox.camoufox_context import CamoufoxContext
from src.utils import normalize_text, save_as
from src.WebFormat import WebTypeA


class IParam(TypedDict):
    link: str
    title: NotRequired[str | None]
    author: NotRequired[str | None]
    source: NotRequired[str | None]
    start: int
    end: int


class Blogspot(WebTypeA):
    def __init__(self, ref: BaseRef, **kwargs: Unpack[IParam]):
        """
        This page index has a different behaviour, hencewhy, it will iterate the chapter url instead of getting the list of indexes.
        Also, generate an html text instead of only text.
        required args:
            - link: str
            - author: str
            - page: Page
            - (optional) start: int = 0
            - end: int
        """
        kwargs["source"] = "UGLYSUNFISH"
        super().__init__(ref, **kwargs)

    async def create(self, hidden: bool = True) -> Path:
        async with CamoufoxContext(headless=hidden) as ctx:
            # chapters
            # await self._get_chapters(ctx)
            await self._download_chapter(ctx)

        return self._files_path

    async def _get_chapters(self, ctx: CamoufoxContext):

        if not self._end:
            return False

        chapters = list(range(self._start, self._end))

        # list of links by chapter
        with tqdm(
            iterable=chapters,
            total=len(chapters),
            desc=f"Collecting",
            unit="chapter",
        ) as pbar:
            for idx, _ in enumerate(pbar, self._start + 1):

                new_chapter = IChapterInfo(
                    title=self.title,
                    author=self.author,
                    page_name=self.source,
                    chapter_link=self.link.format(chapter=idx),
                    chapter_title=f"Chapter {idx}",
                    chapter_number=str(idx),
                )
                self._upsert_chapter_index(new_chapter)

            pbar.set_description("Done collecting")

        return self.save_index_file(self._chap_info)

    async def _get_chapter_content(
        self, ctx: CamoufoxContext, chapter_link: str
    ) -> str:
        await ctx.page.goto(chapter_link, wait_until="domcontentloaded")
        await ctx.page.wait_for_timeout(3000)

        loc_children = await ctx.page.locator(f"{self._content_ref} > *").all()
        html_str: list[str] = [
            val
            for child in loc_children
            if len(val := await child.evaluate("el => el.outerHTML")) > 0
            and not re.search(r"<a\b.*?</a>", val, re.DOTALL)
            and not "href=" in val
        ]

        return "\n".join(html_str)

    async def _download_chapter(self, ctx: CamoufoxContext):
        if not self._content_ref:
            raise ValueError("required chapters paragraph ref not found.")
        chapters = self._chap_info
        with tqdm(
            iterable=chapters,
            total=len(chapters),
            desc="Downloading Chapter",
            unit="chapter",
        ) as pbar:
            for idx, chap in enumerate(pbar, self._start + 1):
                if int(chap.chapter_number) < 306:
                    continue
                pbar.set_description(f"Downloading Chapter {chap.chapter_number}")

                if not chap.chapter_link:
                    continue

                content = await self._get_chapter_content(ctx, chap.chapter_link)

                if not len(content):
                    print(
                        f"Chapter {chap.chapter_number} | {chap.chapter_link} not found."
                    )
                    continue

                chap.file_path = save_as(
                    file_name=f"{idx} {normalize_text(chap.chapter_title)}.txt",
                    file_path=self._chapter_path,
                    file_content=self._get_paragraph(content),
                )
                self._upsert_chapter_index(chap)

                # save chapter details every 10%
                # if int(chap.chapter_number) % 10 == 0:
                self.save_index_file(self._chap_info)

            pbar.set_description("Done downloading")

        self.save_index_file(self._chap_info)
