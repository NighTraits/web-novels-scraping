import asyncio

from src.WebScrapping.SitesScript.novelhi import NovelhiScripting

if __name__ =="__main__":

    asyncio.run(
        # NovelhiScripting(
        #     link="https://novelhi.com/novel/fantasy/true-daughter-she-is-the-almighty-boss", 
        #     author="卿浅"
        # ).create()

        NovelhiScripting(
            link="https://novelhi.com/novel/comedy/my-whole-family-are-villain", 
            author="咸鱼老人"
        ).create()
        
        # NovelhiScripting(
        #     link="https://novelhi.com/novel/fantasy/i-married-the-male-lead-of-a-cp-free-novel", 
        #     author="Ten-tailed Hare (十尾兔)"
        # ).create()
    )
