import re
from typing import Unpack

from src.WebFormat.enums import BaseRef
from src.WebFormat.models import IBase
from src.WebFormat import WebTypeA
from src.WebScrapping import CamoufoxContext


class Wordpress(WebTypeA):
    def __init__(
        self,
        ref: BaseRef,
        **kwargs: Unpack[IBase],
    ):
        """
        Key Word Arguments:
            - link: str
            - author: str
            - page: Page
            - (optional) start: int = 0
            - (optional) end: int
        """
        kwargs["source"] = "wordpress"
        super().__init__(ref, **kwargs)

    async def _get_chapter_content(
        self, ctx: CamoufoxContext, chapter_link: str
    ) -> str:

        await ctx.page.goto(chapter_link, wait_until="networkidle")
        await ctx.page.wait_for_timeout(3000)

        content_ref = ctx.page.locator(f"{self._content_ref}")
        content = "\n".join(await content_ref.all_inner_texts())

        # sometimes, a warning page shows with the real chapter link
        if "Chapter here" in "\n".join(await content_ref.all_inner_texts()):
            await content_ref.get_by_role("link").click()
            await ctx.page.wait_for_timeout(3000)
            content_ref = ctx.page.locator(f"{self._content_ref}")

        raw_content = (
            await ctx.page.locator(f"{self._content_ref}")
            .filter(
                has_not_text=re.compile(
                    r"(sponsor.*chapter.*)|(chapter.*donate|donati)|(reader.*unlock.*)",
                    re.IGNORECASE,
                )
            )
            .all_inner_texts()
        )

        content = "\n".join(raw_content)

        return content
