import asyncio
from scripts import get_from_novelhi, get_from_novlove


async def main():
    await asyncio.gather(
        get_from_novelhi(
            link="link",
        ),
        get_from_novlove(
            link="link",
            author="author",
        ),
    )


if __name__ == "__main__":
    asyncio.run(main())
