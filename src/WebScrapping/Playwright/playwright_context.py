from typing import Self
from playwright.async_api import async_playwright, Browser, Page, Locator, Playwright, BrowserContext
from WebScrapping.models import ILinkInfo

class PlaywrightContext:
    def __init__(self, headless: bool = True) -> None:
        self.headless = headless
        self._playwright: Playwright = None
        self._browser: Browser = None
        self._context: BrowserContext = None
        self._page: Page = None

    async def start(self) -> Self:
        self._playwright = await async_playwright().start()
        self._browser = await self._playwright.chromium.launch(headless=self.headless)

        self._context = await self._browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            # viewport={"width": 1280, "height": 720},
        )
        self._page = await self._context.new_page()
        return self
    
    async def close(self) -> None:
        await self._context.close()
        await self._browser.close()
        await self._playwright.stop()

    async def __aenter__(self):
        return await self.start()

    async def __aexit__(self, *args) -> None:
        # params are required even if not used
        await self.close()
    
    @property
    def browser(self) -> Browser:
        return self._browser

    @property
    def context(self) -> BrowserContext:
        return self._context

    @property
    def page(self) -> Page:
        return self._page