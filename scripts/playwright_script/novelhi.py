import asyncio
from pathlib import Path
from src.utils import dataclass_to_dict, save_as, decode_rot18
from WebScrapping.models import IChapterInfo
from src.WebScrapping.Playwright.playwright_context import PlaywrightContext, Page
from tqdm import tqdm
import json
from src.EpubFile.epub_context import EpubContext
from WebScrapping.SitesScript.actions import Actions

class Novelhi_Web_Scrapping():
    def __init__(self, book_link, author, cover_image):
        self.book_link = book_link
        self.author = author
        self.cover_image = cover_image

        parent_path = Path.cwd()
        self.temp_path = Path(f"{parent_path}/temp")
        self.chapter_path = Path()

    async def download_book(self, home_link:str="https://novelhi.com", source_page:str="novelhi"):
        async with PlaywrightContext(headless=True) as ctx:
            
            self._action = Actions(page=ctx.page)
            
            # # go to url
            await ctx.page.goto(f"{self.book_link}", wait_until='networkidle')

            # get title
            work_info = ctx.page.locator("div.book_info h1")
            work_title = await work_info.inner_text()
            print(f"Title: {work_title}")
            del work_info

            self.temp_path = self.temp_path / f"{work_title} ({source_page})"
            self.chapter_path = self.temp_path / "chapters"
            self.chapter_path.mkdir(parents=True, exist_ok=True)
            
            await self._action.click_element("#chapterList")

            # list of chapters
            chap_dict = await self.get_chapters_link(ctx.page)
            self.store_chapters_details(chap_dict)

            # store chapters as html file
            await self.store_chapters_as_text(ctx.page, chap_dict)
            self.store_chapters_details(chap_dict)

            # create E-Book
            my_book = EpubContext(
                title=work_title, 
                creator=self.author, 
                publisher=source_page, 
                cover=self.cover_image,
                file_path=self.temp_path / f"{work_title} ({source_page}).epub"
            )

            # create E-Book chapter 
            for chap in chap_dict:
                my_book.add_chapter(str(chap.file_path), chap.title)
                # my_book.add_chapter(chapter)

            # my_book.create(str(self.temp_path))
            my_book.create_book()

    async def get_chapters_link(self, page: Page) -> list[IChapterInfo]:
        # get content
        chap_dict: list[IChapterInfo] = []

        chapter_wrapper = page.locator("#indexList")
        chapters = await chapter_wrapper.locator("li.chapter-list-item").all()
        
        # list of links by chapter
        with tqdm(total=len(chapters), desc="Gathering chapters", unit="chapter") as pbar:
            for li in chapters:
                link_info = await self._action.get_link_and_text(li)
                chap_dict.append(IChapterInfo(link_info.text, link_info.href, None))
                pbar.update(1)
            pbar.set_postfix(status='done')
            pbar.close()

        return chap_dict

    async def store_chapters_as_text(self, page: Page, chap_dict: list[IChapterInfo]) -> list[IChapterInfo]:
        with tqdm(total=len(chap_dict), desc="Downloading chapters", unit="chapter") as pbar:
            for idx, chap in enumerate(chap_dict):
                pbar.set_postfix(chapter=idx, status="loading")

                await page.goto(chap.link, wait_until='domcontentloaded')
                try:
                    await page.wait_for_selector('#showReading sent', state='visible')
                    await page.wait_for_timeout(5000)
                except:
                    pass

                paragraph = await page.locator("#showReading sent").all_inner_texts()                
                content = '\n\n'.join(paragraph)

                if "please refresh the page" in content:
                    await page.reload(wait_until='domcontentloaded')

                chap.file_path = save_as(
                    file_name=f"Chapter {idx + 1}.txt",
                    file_path=self.chapter_path,
                    file_content=decode_rot18(content),
                )

                pbar.update(1)
                
            pbar.set_postfix(status='done')
            pbar.close()
            
        return chap_dict

    def store_chapters_details(self, chapters: list[IChapterInfo]):
        chapters_json = dataclass_to_dict(chapters)
        (self.temp_path / 'chapters_details.json').write_text(json.dumps(chapters_json, indent=2))


if __name__=='__main__':

    book_link = "https://novelhi.com/novel/fantasy/true-daughter-she-is-the-almighty-boss"
    cover_image = f"{Path.cwd()}/cover_images/True-Daughter-She-is-the-Almighty-Boss.jpg"
    author = "卿浅"
    
    web_scrapping = Novelhi_Web_Scrapping(book_link, author, cover_image)
    asyncio.run(web_scrapping.download_book())