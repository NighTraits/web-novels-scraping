from dataclasses import dataclass


@dataclass
class ILinkInfo:
    href: str | None
    text: str
