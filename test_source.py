import asyncio

from app.sources.mangadex import MangaDexSource


async def main():

    source = MangaDexSource()

    results = await source.search("Detective Conan")

    manga = results[0]

    print("MANGA:")
    print(f"Title: {manga.title}")
    print(f"ID:    {manga.source_id}")
    print(f"URL:   {manga.url}")

    chapters = await source.get_chapters(manga)

    print(f"\nCHAPTERS FOUND: {len(chapters)}\n")

    for chapter in chapters[:20]:
        print(
            f"Chapter {chapter.chapter_number}"
            f" | {chapter.source_chapter_id}"
            f" | {chapter.title}"
            f" | {chapter.url}"
        )


asyncio.run(main())