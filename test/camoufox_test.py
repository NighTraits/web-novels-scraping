import asyncio
from camoufox.async_api import AsyncCamoufox
from pathlib import Path
import pypub
import shutil

from playwright.async_api import async_playwright
from WebScrapping.models import IChapterInfo

class Novel_Web_Scrapping():
    def __init__(self, book_link, author, cover_image):
        self.book_link = book_link
        self.author = author
        self.cover_image = cover_image

        parent_path = Path.cwd()

        self.temp_path = Path(f"{parent_path}/temp")
        self.chapter_path = Path()

    async def Webnovel(self, home_link:str="https://www.webnovel.com", source_page="webnovel"):
        async with AsyncCamoufox(headless=True) as browser:
            page = await browser.new_page()

            # go to url
            await page.goto(f"{self.book_link}")
            
            # get title
            work_info = page.locator("[class*='det-info'] h1")
            work_title = await work_info.inner_text()
            print(f"Title: {work_title}")
            del work_info

            self.temp_path = self.temp_path / f"{work_title} ({source_page})"
            self.chapter_path = self.temp_path / "chapters"
            self.chapter_path.mkdir(parents=True, exist_ok=True)

            # get content
            chap_dict: list[IChapterInfo] = []
            
            chapter_wrapper = page.locator("div.volume-item")
            chapters = await chapter_wrapper.locator("[class*='col']").all()
            
            # list of links by chapter
            for li in chapters:
                li_link = li.get_by_role("link")
                chap_title = await li_link.get_attribute("title")
                chapter_link = await li_link.get_attribute("href")
                chap_dict.append(IChapterInfo(chap_title, chapter_link, None))
            
            # concat paragraphs by chapter
            for idx, chap in enumerate(chap_dict):
                await page.goto(f"{home_link}{chap.link}")
                paragraph = await page.locator("[class*='cha-paragraph']").all_inner_texts()
                content = "\n\n".join(paragraph)
                
                # store chapter
                file_path: Path = self.chapter_path / f"Chapter_{idx + 1}.txt"
                file_path.write_text(content, encoding="utf-8")
                chap.file_path = file_path

            # delete existing book
            self.temp_path = self.temp_path / f"{work_title} ({source_page}).epub"
            if self.temp_path.exists():
                self.temp_path.unlink()

            # create E-Book
            my_book = pypub.Epub(
                title=work_title, 
                creator=self.author, 
                publisher=source_page, 
                cover=self.cover_image,
            )

            # create E-Book chapter 
            for chap in chap_dict:
                chapter = pypub.create_chapter_from_file(str(chap.file_path), chap.title)
                my_book.add_chapter(chapter)

            my_book.create(str(self.temp_path))

            # shutil.rmtree(self.chapter_path)

book_link = "https://www.webnovel.com/book/19414072706404905/catalog"
cover_image = f"{Path.cwd()}/cover_images/True-Daughter-She-is-the-Almighty-Boss.jpg"
author = "卿浅"
web_scrapping = Novel_Web_Scrapping(book_link, author, cover_image)
asyncio.run(web_scrapping.Webnovel())
