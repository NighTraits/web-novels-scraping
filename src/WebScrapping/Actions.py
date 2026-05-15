from pathlib import Path
from playwright.async_api import Locator, Page
from src.WebScrapping.models import ILinkInfo
import requests, io
from PIL import Image


async def click_element(page: Page, element_ref: str | Locator, timeout: int = 5000):
    if not isinstance(element_ref, Locator):
        element_ref = page.locator(element_ref)
    await element_ref.click()
    await page.wait_for_load_state("networkidle")
    await page.wait_for_timeout(timeout)


async def get_link_and_text(page: Page, element_ref: Locator | str) -> ILinkInfo:
    if not isinstance(element_ref, Locator):
        element_ref = page.locator(element_ref)

    link_elem = element_ref.get_by_role("link")
    text = await link_elem.inner_text()
    href = await link_elem.get_attribute("href")
    return ILinkInfo(href=href, text=text)


async def screenshot(page: Page, file_path: Path):
    """screenshot entire page"""
    await page.screenshot(path=file_path)


async def capture_element(page: Page, element_ref: Locator | str, file_path: Path):
    """screen capture an element (image, div, etc)"""
    if not isinstance(element_ref, Locator):
        element_ref = page.locator(element_ref)

    await element_ref.screenshot(path=file_path)


async def save_image(page: Page, element_ref: Locator | str, file_path: Path):
    if not isinstance(element_ref, Locator):
        element_ref = page.locator(element_ref)

    link = await element_ref.get_attribute("src")
    if not link:
        return

    response = requests.get(link).content
    image_file = io.BytesIO(response)
    image = Image.open(image_file)
    image.save(file_path, "png")
