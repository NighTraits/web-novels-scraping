from pathlib import Path
import re
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

    if await element_ref.evaluate("el => el.tagName.toLowerCase()") != "a":
        element_ref = element_ref.get_by_role("link")

    text = [
        txt
        for txt in str(await element_ref.inner_text()).split("\n")
        if not re.search(
            r"\d+\s+(?:years?|months?|days?|hours?|minutes?|seconds?)",
            txt,
            re.IGNORECASE,
        )
    ]

    href = await element_ref.evaluate("el => el.href")

    return ILinkInfo(href=href, text=" ".join(text))


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

    link = await element_ref.evaluate("el => el.src")
    if not link:
        return None

    response = requests.get(link).content
    image_file = io.BytesIO(response)
    image = Image.open(image_file)
    image.save(file_path, "png")


async def toggle_chapters_list_button(page: Page) -> None:
    btn = (
        page.locator("button, a ")
        .filter(
            has_text=re.compile(
                r"(?:table of contents?|toc|chapters|chapters lists?)\s*", re.IGNORECASE
            )
        )
        .first
    )

    if await btn.is_visible(timeout=1000):
        await btn.click()


async def get_novel_cover(page: Page, file_path: Path):
    img_ref = await page.locator("img[src]:not(header *, footer *)").get_attribute(
        "src"
    )
    print(img_ref)
