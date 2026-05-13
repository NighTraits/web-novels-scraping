import asyncio
import json
from pathlib import Path
import re
from playwright.async_api import Page
from src.WebScrapping.Camoufox.camoufox_context import CamoufoxContext
from WebScrapping.models import IChapterInfo
from src.EpubFile.epub_context import EpubContext
from WebScrapping.SitesScript.actions import Actions
from tqdm import tqdm

from src.utils import clean_paragraph, dataclass_to_dict, decode_rot18, save_as

class Novelhi_Camoufox:
    def __init__(self, book_link: str, author, cover_image):
        self.book_link = book_link
        self.author = author
        self.cover_image = cover_image

        parent_path = Path.cwd()
        self.temp_path = Path(f"{parent_path}/temp")
        self.chapter_path = Path()

        self.details_file = Path()

    async def download_book(self, source_page:str="novelhi"):
        async with CamoufoxContext(headless=True) as ctx:
            self._action = Actions(page=ctx.page)
            await ctx.page.goto(f"{self.book_link}", wait_until='networkidle')

            # get title
            work_info = ctx.page.locator("div.book_info h1")
            work_title = await work_info.inner_text()
            print(f"Title: {work_title}")
            del work_info

            self.temp_path = self.temp_path / f"{work_title} ({source_page})"
            self.chapter_path = self.temp_path / "chapters"
            self.chapter_path.mkdir(parents=True, exist_ok=True)
            # chapters details list
            self.details_file = self.temp_path / 'chapters_details.json'

            await self._action.click_element("#chapterList")

            # list of chapters
            chap_dict = await self.get_chapters_link(ctx.page)

            # store chapters as html file
            await self.store_chapters_as_text(ctx.page, chap_dict[751:])
            
            EpubContext(
                title=work_title, 
                creator=self.author, 
                publisher=source_page, 
                cover=self.cover_image,
                file_path=self.temp_path / f"{work_title} ({source_page}).epub"
            ).files_to_epub(chap_dict)

    async def get_chapters_link(self, page: Page) -> list[IChapterInfo]:
        # get content
        chap_dict: list[IChapterInfo] = []
        chapters = await page.locator("#indexList li.chapter-list-item").all()
        
        # list of links by chapter
        with tqdm(total=len(chapters), desc="Gathering chapters", unit="chapter") as pbar:
            for li in chapters:
                link_info = await self._action.get_link_and_text(li)
                chap_num = re.search(r'\d+', link_info.text).group(0)
                chap_dict.append(IChapterInfo(
                    title=link_info.text, 
                    chapter=chap_num,
                    link=link_info.href, 
                    file_path=None
                ))
                pbar.update(1)
            pbar.set_postfix(status='done')
            pbar.close()
        
        # save chapters data
        self.store_chapters_details(chap_dict)
        
        return chap_dict

    async def store_chapters_as_text(self, page: Page, chap_dict: list[IChapterInfo]) -> list[IChapterInfo]:
        with tqdm(total=len(chap_dict), desc="Downloading chapters", unit="chapter") as pbar:
            for chap in chap_dict:
                pbar.set_postfix(chapter=chap.chapter, status="loading")

                ### fix
                await page.goto(chap.link, wait_until='domcontentloaded')
                await page.wait_for_function(
                    "document.querySelectorAll('#showReading *').length > 5",
                    polling=3000
                )
                await page.wait_for_timeout(3000)

                paragraph = await page.locator("#showReading").inner_text()

                chap.file_path = save_as(
                    file_name=f"Chapter {chap.chapter}.txt",
                    file_path=self.chapter_path,
                    file_content=clean_paragraph(decode_rot18(paragraph)),
                )

                pbar.update(1)
                
                # save chapter details every 10%
                if int(chap.chapter) % 10 == 0:
                    self.store_chapters_details(chap_dict)
                
            pbar.set_postfix(status='done')
            pbar.close()
            
        return chap_dict

    def store_chapters_details(self, chapters: list[IChapterInfo]):
        chapters_json = dataclass_to_dict(chapters)
        self.details_file.write_text(json.dumps(chapters_json, indent=2))

if __name__ =="__main__":

    
    book_link = "https://novelhi.com/novel/fantasy/true-daughter-she-is-the-almighty-boss"
    cover_image = Path("assets/True-Daughter-She-is-the-Almighty-Boss.jpg")
    author = "卿浅"
    
    web_scrapping = Novelhi_Camoufox(book_link, author, cover_image)
    asyncio.run(web_scrapping.download_book())