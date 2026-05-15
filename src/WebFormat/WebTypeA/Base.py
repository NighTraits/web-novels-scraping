from pathlib import Path
import re
from tqdm import tqdm
from typing import Unpack, final
from src.WebFormat.Book import BookContext
from src.WebFormat.models import IBase, IChapterInfo
from src.WebScrapping import (
    CamoufoxContext,
    click_element,
    get_link_and_text,
    save_image,
)
from src.WebScrapping.models import ILinkInfo
from src.utils import clean_paragraph, save_as


class WebTypeA(BookContext):
    def __init__(self, **kwargs: Unpack[IBase]):
        """
        required args:
            - link: str
            - author: str
            - page: Page
            - (optional) start: int = 0
            - (optional) end: int
        """
        super().__init__(**kwargs)

        self._title_ref: str | None = None
        self.__chapter_tab_ref: list[str] | None = None
        self._chapter_index_ref: str | None = None
        self._content_ref: str | None = None
        self._book_cover_ref: str | None = None

    @final
    def _set_chapter_tab_ref(self, ref: str | None):
        if not ref:
            return
        self.__chapter_tab_ref = [tab.strip() for tab in ref.split(",")]

    async def create(self, hidden: bool = True) -> Path:
        async with CamoufoxContext(headless=hidden) as ctx:
            await ctx.page.goto(f"{self.link}", wait_until="networkidle")

            # book descriptions
            await self._get_title_and_cover(ctx)

            # chapters
            await self._get_chapters_ref(ctx)
            await self._download_chapter(ctx)

        return self._files_path

    async def _get_title_and_cover(self, ctx: CamoufoxContext):
        await self._get_title(ctx)
        await self._get_cover(ctx)

    async def _get_title(self, ctx: CamoufoxContext):
        print("Retrieving book title...")
        if not self._title_ref:
            raise ValueError("required title ref not found.")
        work_title = await ctx.page.locator(self._title_ref).first.inner_text()
        self.set_title_and_create_directory(work_title.title())
        print(f"Title: {self.title}")

    async def _get_cover(self, ctx: CamoufoxContext):
        print("Retrieving book cover...")
        if not self._book_cover_ref:
            raise ValueError("required book cover ref not found.")

        if self.cover.exists():
            return

        await save_image(ctx.page, self._book_cover_ref, self.cover)

    async def _get_chapters_ref(self, ctx: CamoufoxContext):
        if not self._chapter_index_ref:
            raise ValueError("required chapters index ref not found.")

        # clicks needed to access the index
        if self.__chapter_tab_ref:
            for tab in self.__chapter_tab_ref:
                await click_element(ctx.page, tab)

        # get content
        chapters = await ctx.page.locator(self._chapter_index_ref).all()
        chapters = chapters[self._start : self._end]

        # list of links by chapter

        with tqdm(
            iterable=chapters,
            total=len(chapters),
            desc=f"Collecting",
            unit="chapter",
        ) as pbar:
            for idx, li in enumerate(pbar, self._start):
                link_info: ILinkInfo = await get_link_and_text(ctx.page, li)

                if chap_num := re.search(r"\d+", link_info.text):
                    chap_num = int(chap_num.group(0))

                new_chapter = IChapterInfo(
                    title=self.title,
                    author=self.author,
                    page_name=self.source,
                    chapter_link=link_info.href,
                    chapter_title=link_info.text,
                    chapter_number=chap_num or (idx + 1),
                    file_path=None,
                )
                self.__upsert_chapter_index(new_chapter)

            pbar.set_description("Done collecting")

        return self.save_index_file(self._chap_info)

    def _get_paragraph(self, text: str) -> str:
        return clean_paragraph(text)

    async def _download_chapter(self, ctx: CamoufoxContext):
        if not self._content_ref:
            raise ValueError("required chapters paragraph ref not found.")
        chapters = self._chap_info[self._start : self._end]
        with tqdm(
            iterable=chapters,
            total=len(chapters),
            desc="Downloading Chapter",
            unit="chapter",
        ) as pbar:

            for chap in pbar:
                pbar.set_description(f"Downloading Chapter {chap.chapter_number}")

                if not chap.chapter_link:
                    continue

                await ctx.page.goto(chap.chapter_link, wait_until="networkidle")
                await ctx.page.wait_for_function(
                    f"document.querySelectorAll('{self._content_ref} *').length > 5",
                    polling=3000,
                )
                await ctx.page.wait_for_timeout(3000)

                content = await ctx.page.locator(f"{self._content_ref}").inner_text()

                chap.file_path = save_as(
                    file_name=f"Chapter {chap.chapter_number}.txt",
                    file_path=self._chapter_path,
                    file_content=self._get_paragraph(content),
                )
                self.__upsert_chapter_index(chap)

                # save chapter details every 10%
                if int(chap.chapter_number) % 10 == 0:
                    self.save_index_file(self._chap_info)

            pbar.set_description("Done downloading")

        self.save_index_file(self._chap_info)

    def __upsert_chapter_index(self, update_data: IChapterInfo):
        if any(
            chap.chapter_number == update_data.chapter_number
            for chap in self._chap_info
        ):
            for idx, chap in enumerate(self._chap_info):
                if chap.chapter_number != update_data.chapter_number:
                    continue
                self._chap_info[idx] = update_data
                break
        else:
            self._chap_info.append(update_data)
