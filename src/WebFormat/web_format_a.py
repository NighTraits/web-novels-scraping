from pathlib import Path
from playwright.async_api import Locator, Page
from tqdm import tqdm
from typing import List, Unpack, final
from src.WebFormat.enums import BaseRef, EOrder
from src.WebFormat.Book import BookContext
from src.WebFormat.models import IBase, IChapterInfo
from src.WebScrapping import (
    CamoufoxContext,
    click_element,
    get_link_and_text,
    save_image,
)
from src.WebScrapping.models import ILinkInfo
from src.models import UNKNOWN
from src.utils import clean_paragraph, save_as


class WebTypeA(BookContext):
    def __init__(self, ref: BaseRef, **kwargs: Unpack[IBase]):
        """
        required args:
            - link: str
            - author: str
            - page: Page
            - (optional) start: int = 0
            - (optional) end: int
        """
        super().__init__(**kwargs)

        self.__chapter_tab_ref: list[str] | None = None
        self._title_ref = ref.TITLE_DIV
        self._chapter_index_ref = ref.CHAPTER_INDEX
        self._content_ref = ref.CONTENT_ID
        self._book_cover_ref = ref.COVER_IMG
        self._set_chapter_tab_ref(ref.CHAPTER_TAB_ID)

    @final
    def _set_chapter_tab_ref(self, ref: str | None):
        if not ref:
            return
        self.__chapter_tab_ref = [tab.strip() for tab in ref.split(",")]

    @final
    async def __get_visible_chapters_count(self, page: Page) -> int:
        if not self._chapter_index_ref:
            return 0
        return len(await page.locator(self._chapter_index_ref).all())

    async def create(self, hidden: bool = True) -> Path:
        async with CamoufoxContext(headless=hidden) as ctx:
            await ctx.page.goto(f"{self.link}", wait_until="networkidle")
            await ctx.page.wait_for_timeout(5000)

            # book descriptions
            await self._get_title_and_cover(ctx)

            # chapters
            await self._get_chapters(ctx)
            await self._download_chapter(ctx)

        return self._files_path

    async def _get_title_and_cover(self, ctx: CamoufoxContext):
        await self._get_title(ctx)
        await self._get_cover(ctx)

    async def _get_title(self, ctx: CamoufoxContext):
        if self.title != UNKNOWN:
            return

        print("Retrieving book title...")

        if not self._title_ref:
            raise ValueError("required title ref not found.")

        work_title = await ctx.page.locator(self._title_ref).first.inner_text()
        self.set_title_and_create_directory(work_title.title())
        print(f"Title: {self.title}")

    async def _get_cover(self, ctx: CamoufoxContext):
        if self.cover.exists() or not self._book_cover_ref:
            return

        print("Retrieving book cover...")

        await save_image(ctx.page, self._book_cover_ref, self.cover)

    async def _show_chapter_index(self, page: Page, current_count: int):
        """
        - click and compare the amount of chapters shown
        - if it's less than before, click again
        - if it's the same amount, continue with the next
        """
        if not self.__chapter_tab_ref or not self._chapter_index_ref:
            return

        for tab in self.__chapter_tab_ref:
            sub_tab = await page.locator(tab).all()
            for st in sub_tab:
                await click_element(page, st)
                if await self.__get_visible_chapters_count(page) < current_count:
                    await click_element(page, st)

    async def _get_index(self, page: Page) -> list[Locator]:
        if not self._chapter_index_ref:
            raise ValueError("required chapters index ref not found.")

        counts = await self.__get_visible_chapters_count(page)
        await self._show_chapter_index(page, counts)

        # get content
        content = await page.locator(self._chapter_index_ref).all()

        if self._chapter_order == EOrder.DESC:
            content.reverse()

        return content

    async def _get_chapters(self, ctx: CamoufoxContext):

        chapters = await self._get_index(ctx.page)

        """
            optimize this method as it just split the chapters list by index instead of the chapter number
            1. split by finding the chapter number
            2. asc and desc order detection
        """
        chapters = chapters[self._start : self._end]

        for chapter in chapters:
            link_info: ILinkInfo = await get_link_and_text(ctx.page, chapter)

        # list of links by chapter
        with tqdm(
            iterable=chapters,
            total=len(chapters),
            desc=f"Collecting",
            unit="chapter",
        ) as pbar:
            for idx, li in enumerate(pbar, self._start + 1):
                link_info: ILinkInfo = await get_link_and_text(ctx.page, li)

                # if chap_num := re.search(r"[-|\d]+", link_info.text):
                #     chap_num = chap_num.group(0)

                new_chapter = IChapterInfo(
                    title=self.title,
                    author=self.author,
                    page_name=self.source,
                    chapter_link=link_info.href,
                    chapter_title=link_info.text,
                    chapter_number=str(idx),
                )
                self._upsert_chapter_index(new_chapter)

            pbar.set_description("Done collecting")

        return self.save_index_file(self._chap_info)

    def _get_paragraph(self, text: str) -> str:
        return clean_paragraph(text)

    async def _get_chapter_content(
        self, ctx: CamoufoxContext, chapter_link: str
    ) -> str:
        await ctx.page.goto(chapter_link, wait_until="domcontentloaded")
        # await ctx.page.wait_for_function(
        #     f"document.querySelectorAll('{self._content_ref} *').length > 5",
        #     polling=3000,
        # )
        await ctx.page.wait_for_timeout(3000)
        list_text = await ctx.page.locator(f"{self._content_ref}").all_inner_texts()

        return "\n".join(list_text)

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

            for idx, chap in enumerate(pbar, self._start + 1):
                pbar.set_description(f"Downloading Chapter {chap.chapter_number}")

                if not chap.chapter_link:
                    continue

                content = await self._get_chapter_content(ctx, chap.chapter_link)

                if not len(content):
                    print(
                        f"Chapter {chap.chapter_number} | {chap.chapter_link} not found."
                    )
                    continue

                chap.file_path = self._chapter_path / f"Chapter {idx}.txt"
                save_as(
                    file_path=self._files_path / chap.file_path,
                    file_content=self._get_paragraph(content),
                )
                self._upsert_chapter_index(chap)

                # save chapter details every 10%
                # if int(chap.chapter_number) % 10 == 0:
                self.save_index_file(self._chap_info)

            pbar.set_description("Done downloading")

        self.save_index_file(self._chap_info)

    def _upsert_chapter_index(self, update_data: IChapterInfo):
        if current := next(
            (
                idx
                for idx, chap in enumerate(self._chap_info)
                if chap.chapter_number == update_data.chapter_number
                and chap.chapter_title == update_data.chapter_title
            ),
            None,
        ):
            if not update_data.file_path:
                update_data.file_path = self._chap_info[current].file_path
            self._chap_info[current] = update_data

        else:
            self._chap_info.append(update_data)
