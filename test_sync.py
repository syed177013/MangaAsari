import asyncio

from sqlalchemy import select

from app.anilist import search_manga
from app.database import SessionLocal
from app.models import Manga
from app.sources.mangadex import MangaDexSource
from app.sources.base import SourceManga
from app.services.sync import sync_manga_source


async def main():

    # Get Detective Conan from AniList.
    results = await search_manga("Meitantei Conan")

    manga_data = next(
        manga
        for manga in results
        if manga["id"] == 41176
    )

    # Update the existing MangaAsari record.
    with SessionLocal() as db:

        manga = db.scalar(
            select(Manga).where(
                Manga.anilist_id == 41176
            )
        )

        if manga is None:
            raise ValueError(
                "Detective Conan is not in the database."
            )

        manga.title = (
            manga_data["title"]["english"]
            or manga_data["title"]["romaji"]
            or manga_data["title"]["native"]
            or "Unknown"
        )

        manga.romaji_title = (
            manga_data["title"]["romaji"]
        )

        manga.native_title = (
            manga_data["title"]["native"]
        )

        manga.aliases = (
            " | ".join(manga_data["synonyms"])
            if manga_data.get("synonyms")
            else None
        )

        manga.cover_url = (
            manga_data["coverImage"]["medium"]
            if manga_data.get("coverImage")
            else None
        )

        manga.status = manga_data["status"]

        db.commit()

        manga_id = manga.id

    # Sync chapters from MangaDex.
    source = MangaDexSource()

    source_manga = SourceManga(
        source_id="7f30dfc3-0b80-4dcc-a3b9-0cd746fac005",
        title="Meitantei Conan",
        url=(
            "https://mangadex.org/title/"
            "7f30dfc3-0b80-4dcc-a3b9-0cd746fac005"
        ),
    )

    result = await sync_manga_source(
        manga_id=manga_id,
        source=source,
        source_manga=source_manga,
    )

    print(result)


asyncio.run(main())