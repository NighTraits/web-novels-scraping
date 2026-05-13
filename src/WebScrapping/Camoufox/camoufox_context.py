from pathlib import Path
from typing import Any, Self
from camoufox.async_api import AsyncCamoufox
from playwright.async_api import Browser, BrowserContext, Locator, Page
from src.WebScrapping.models import ILinkInfo


class CamoufoxContext:
    def __init__(self, headless: bool = True) -> None:
        self.headless = headless

        self._camoufox: AsyncCamoufox
        self._browser: Browser | BrowserContext
        self._context: BrowserContext
        self._page: Page

    async def __aenter__(self) -> Self:
        self._camoufox = AsyncCamoufox(headless=self.headless, window=(720, 720))
        self._browser = await self._camoufox.__aenter__()
        # self._context = await self._browser.new_context()
        self._page = await self._browser.new_page()

        return self

    async def __aexit__(self, *args: Any) -> None:
        # if self._context:
        #     await self._context.close()
        if self._camoufox:
            # await self._camoufox.__aexit__(exc_type, exc_val, exc_tb)
            await self._camoufox.__aexit__(*args)

    @property
    def browser(self) -> Browser | BrowserContext:
        return self._browser

    # @property
    # def context(self) -> BrowserContext:
    #     return self._context

    @property
    def page(self) -> Page:
        return self._page

    async def click_element(self, element_ref: str | Locator, timeout: int = 5000):
        if not isinstance(element_ref, Locator):
            element_ref = self._page.locator(element_ref)
        await element_ref.click()
        await self._page.wait_for_load_state("networkidle")
        await self._page.wait_for_timeout(timeout)

    async def get_link_and_text(self, element_ref: Locator | str) -> ILinkInfo:
        if not isinstance(element_ref, Locator):
            element_ref = self._page.locator(element_ref)

        link_elem = element_ref.get_by_role("link")
        text = await link_elem.inner_text()
        href = await link_elem.get_attribute("href")
        return ILinkInfo(href=href, text=text)

    async def save_image(self, element_ref: str, file_path: Path):

        await self._page.locator(element_ref).screenshot(path=file_path)

        # # can also screenshot entire page
        # await page.screenshot(path="page.png")
