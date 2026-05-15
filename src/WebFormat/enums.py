from dataclasses import dataclass
from enum import StrEnum


@dataclass
class BaseRef:
    COVER_IMG: str | None = None
    TITLE_DIV: str | None = None
    CHAPTER_TAB_ID: str | None = None
    CHAPTER_INDEX: str | None = None
    CONTENT_ID: str | None = None


class EOrder(StrEnum):
    ASC = "asc"
    DESC = "desc"


WEBNOVEL = BaseRef(
    COVER_IMG="div.det-info img[src]",
    TITLE_DIV="div.det-info div.df h1",
    CHAPTER_TAB_ID="div.det-tab-nav a[href].j_show_contents",
    CHAPTER_INDEX="div.volume-item a[href]",
    CONTENT_ID="div.cha-content div.cha-words p",
)

NOVELHI = BaseRef(
    COVER_IMG="a.book_cover img.cover",
    TITLE_DIV="div.book_info h1",
    CHAPTER_TAB_ID="#chapterList",
    CHAPTER_INDEX="#indexList li.chapter-list-item",
    CONTENT_ID="#showReading",
)

NOVLOVE = BaseRef(
    COVER_IMG="div.book img.lazy",
    TITLE_DIV="div.desc h3.title",
    CHAPTER_TAB_ID="#tab-chapters-title",
    CHAPTER_INDEX="#list-chapter ul.list-chapter li",
    CONTENT_ID="#chr-content",
)

WORDPRESS_FOUR_SEASONS_FOREST = BaseRef(
    CHAPTER_INDEX="figure.wp-block-table a",
    CONTENT_ID="div.entry-content p.wp-block-paragraph",
)

WORDPRESS_REVERIE_DE_FLEURS = BaseRef(
    COVER_IMG="div.entry-content figure.wp-block-image img",
    CHAPTER_INDEX="div.entry-content ul.wp-block-list a",
    CONTENT_ID="div.entry-content p.wp-block-paragraph",
)


WORDPRESS_MENTOLTRANS = BaseRef(
    TITLE_DIV="h2.wp-block-post-title",
    CHAPTER_INDEX="div.wp-block-group ul.wp-block-list a",
    CONTENT_ID="div.entry-content p.wp-block-paragraph:not(:has(*))",
)

GENERIC_RUBY_MAYBE = BaseRef(
    # CHAPTER_TAB_ID="div.nv-content-wrap details",
    CHAPTER_INDEX="div.nv-content-wrap details p a",
    CONTENT_ID="div.nv-content-wrap p:not(:has(>a))",
)

BLOGSPOT = BaseRef(
    CONTENT_ID="div.post-body",
)

READHIVE = BaseRef(
    COVER_IMG='img[x-ref="art"]',
    CHAPTER_TAB_ID='a[href="#releases"]',
    CHAPTER_INDEX="""div[x-show="tab === 'releases'"] a[href]""",
    CONTENT_ID="""div.prose p""",
)
