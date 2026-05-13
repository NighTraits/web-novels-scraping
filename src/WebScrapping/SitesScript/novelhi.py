import os
import re
from dotenv import load_dotenv
from pathlib import Path
from tqdm import tqdm
from typing import Unpack
from WebScrapping.Camoufox import CamoufoxContext
from WebScrapping.models import INovelhi, ELOADSTATE, IChapterInfo, ILinkInfo
from WebScrapping.SitesScript.book import BookContext
from utils import clean_paragraph, decode_rot18, save_as

class NovelhiScripting(BookContext):
    def __init__(self, **kwargs: Unpack[INovelhi]):
        """
            required args:
                - link: str
                - author: str
                - page: Page 
                - (optional) start: int = 0
                - (optional) end: int
        """
        super().__init__(**kwargs, source="novelhi")
        
        load_dotenv()

        self._title_ref = os.getenv("NOVELHI_TITLE_DIV")
        self._index_tab = os.getenv("NOVELHI_CHAPTER_TAB_ID")
        self._index_ref = os.getenv("NOVELHI_CHAPTER_INDEX")
        self._content_ref = os.getenv("NOVELHI_CONTENT_ID")

        self._chap_info: list[IChapterInfo] = []

        self._start: int = kwargs.get("start")
        self._end: int = kwargs.get("end")

    async def create(self, hidden: bool = True):

        self.to_epub(Path("temp\My Whole Family Are Villain (novelhi)\index.json"))
        # async with CamoufoxContext(headless=hidden) as ctx:
        #     await ctx.page.goto(f"{self.link}", wait_until=ELOADSTATE.NETWORKIDLE)

        #     # book descriptions
        #     await self.get_title(ctx)
        #     await self.get_cover(ctx)

        #     # chapters
        #     await self.get_chapters_ref(ctx)
        #     await self.download_chapter(ctx)


    async def get_title(self, ctx: CamoufoxContext):
        work_title = await ctx.page.locator(self._title_ref).inner_text()
        self.set_title_and_create_directory(work_title)
        print(f"Title: {self.title}")

    async def get_cover(self, ctx: CamoufoxContext):
        self.set_cover("book-cover.png")
        print(self.cover)
        await ctx.save_image("a.book_cover img.cover", self.cover)

    async def get_chapters_ref(self, ctx: CamoufoxContext) -> Path | None:
        # get content
        await ctx.click_element(self._index_tab)
        chapters = await ctx.page.locator(self._index_ref).all()

        # list of links by chapter
        with tqdm(total=len(chapters), desc=f"{self.title}: Gathering indexes...", unit="chapter") as pbar:
            pbar.set_postfix(status='loading')

            for li in chapters:
                link_info: ILinkInfo = await ctx.get_link_and_text(li)
                chap_num = re.search(r'\d+', link_info.text).group(0)
                self._chap_info.append(IChapterInfo(
                    title=link_info.text, 
                    chapter=chap_num,
                    link=link_info.href, 
                    file_path=None
                ))
                pbar.update(1)
            
            pbar.set_postfix(status='done')
            pbar.close()
        
        return self.save_index_file(self._chap_info)
    
    async def download_chapter(self, ctx: CamoufoxContext):
        with tqdm(total=len(self._chap_info), desc="Downloading chapters", unit="chapter") as pbar:
            for chap in self._chap_info:
                pbar.set_postfix(chapter=chap.chapter, status="loading")

                ### fix
                await ctx.page.goto(chap.link, wait_until='domcontentloaded')
                await ctx.page.wait_for_function(
                    "document.querySelectorAll('#showReading *').length > 5",
                    polling=3000
                )
                await ctx.page.wait_for_timeout(3000)

                paragraph = await ctx.page.locator("#showReading").inner_text()

                chap.file_path = save_as(
                    file_name=f"Chapter {chap.chapter}.txt",
                    file_path=self._chapter_path,
                    file_content=clean_paragraph(decode_rot18(paragraph)),
                )

                pbar.update(1)
                
                # save chapter details every 10%
                if int(chap.chapter) % 10 == 0:
                    self.save_index_file(self._chap_info)
                
            pbar.set_postfix(status='done')
            pbar.close()
