import asyncio

from app.sources.mangadex import MangaDexSource


async def main():

    source = MangaDexSource()

    results = await source.search("Magic Kaito")

    print(f"Found {len(results)} results:\n")

    for manga in results:

        print(f"Title: {manga.title}")
        print(f"Source ID: {manga.source_id}")
        print(f"URL: {manga.url}")
        print()


asyncio.run(main())