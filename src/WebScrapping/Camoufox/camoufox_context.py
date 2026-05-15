from typing import Any, Self
from camoufox.async_api import AsyncCamoufox
from playwright.async_api import Browser, BrowserContext, Page


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
