import asyncio

from app.sources.mangadex import MangaDexSource
from app.sources.base import SourceManga


async def main():

    source = MangaDexSource()

    manga = SourceManga(
        source_id="247fe684-e74b-42f9-ae63-0c410a663408",
        title="Magic Kaito",
        url=(
            "https://mangadex.org/title/"
            "247fe684-e74b-42f9-ae63-0c410a663408"
        ),
    )

    chapters = await source.get_chapters(manga)

    print(f"\nFound {len(chapters)} chapters.\n")

    for chapter in chapters[:10]:

        print(
            f"Chapter {chapter.chapter_number}"
            f" | {chapter.title}"
            f" | {chapter.source_chapter_id}"
        )


asyncio.run(main())