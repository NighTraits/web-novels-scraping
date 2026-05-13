from playwright.async_api import Page, Locator
from WebScrapping.models import ILinkInfo

class Actions():
    def __init__(self, page: Page):
        self._page = page
        
    async def click_element(self, elem: Locator | str, timeout: int = 3000):
        if not isinstance(elem, Locator):
            elem = self._page.locator(elem)
        await elem.click()
        await self._page.wait_for_load_state('networkidle')
        await self._page.wait_for_timeout(timeout)

    async def get_link_and_text(self, elem: Locator | str) -> ILinkInfo:
        if not isinstance(elem, Locator):
            elem = self._page.locator(elem)
        link_elem = elem.get_by_role("link")
        text = await link_elem.inner_text()
        href = await link_elem.get_attribute("href")
        return ILinkInfo(href=href, text=text)