import asyncio
from playwright.async_api import async_playwright
from pathlib import Path
import pypub
from WebScrapping.models import IChapterInfo
import shutil

from tqdm import tqdm

class Novel_Web_Scrapping():
    def __init__(self, book_link, author, cover_image):
        self.book_link = book_link
        self.author = author
        self.cover_image = cover_image

        parent_path = Path.cwd()

        self.temp_path = Path(f"{parent_path}/temp2")
        self.chapter_path = Path()


    async def Novelhi(self, home_link:str="https://novelhi.com", source_page:str="novelhi"):
        async with async_playwright() as play:
            browser = await play.chromium.launch(headless=False)
            context = await browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
                # viewport={"width": 1280, "height": 720},
            )
            
            # # If still detected, add the webdriver flag patch
            # await page.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

            page = await context.new_page()

            # go to url
            await page.goto(f"{self.book_link}", wait_until='networkidle')

            # get title
            work_info = page.locator("div.book_info h1")
            work_title = await work_info.inner_text()
            print(f"Title: {work_title}")
            del work_info

            self.temp_path = self.temp_path / f"{work_title} ({source_page})"
            self.chapter_path = self.temp_path / "chapters"
            self.chapter_path.mkdir(parents=True, exist_ok=True)

            # click on show all chapters tab
            await page.locator("#chapterList").click()
            await page.wait_for_load_state('networkidle')
            await page.wait_for_timeout(3000)
            
            # get content
            chap_dict: list[IChapterInfo] = []

            chapter_wrapper = page.locator("#indexList")
            chapters = await chapter_wrapper.locator("li.chapter-list-item").all()
            
            # list of links by chapter
            for li in chapters:
                
                li_link = li.get_by_role("link")
                chap_title = await li_link.inner_text()
                chapter_link = await li_link.get_attribute("href")

                chap_dict.append(IChapterInfo(chap_title, chapter_link, None))
            
            # concat paragraphs by chapter
            
            for idx, chap in enumerate(chap_dict):
                
                await page.goto(chap.link)
                await page.wait_for_load_state('networkidle')
                await page.wait_for_timeout(3000)

                paragraph = await page.locator("#showReading sent").all_inner_texts()
                content = "\n\n".join(paragraph)

                #store chapter
                file_path: Path = self.chapter_path / f"Chapter {idx + 1}.txt"
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


book_link = "https://novelhi.com/novel/fantasy/true-daughter-she-is-the-almighty-boss"
cover_image = f"{Path.cwd()}/cover_images/True-Daughter-She-is-the-Almighty-Boss.jpg"
author = "卿浅"
web_scrapping = Novel_Web_Scrapping(book_link, author, cover_image)
asyncio.run(web_scrapping.Novelhi())