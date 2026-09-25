from sqlalchemy import select

from app.database import SessionLocal
from app.models import Manga, Source, MangaSourceMapping


with SessionLocal() as db:
    manga = db.scalar(
        select(Manga).where(Manga.title == "Magic Kaito")
    )

    source = db.scalar(
        select(Source).where(Source.key == "mangadex")
    )

    if manga is None:
        raise RuntimeError("Magic Kaito not found")

    if source is None:
        raise RuntimeError("MangaDex source not found")

    existing = db.scalar(
        select(MangaSourceMapping).where(
            MangaSourceMapping.manga_id == manga.id,
            MangaSourceMapping.source_id == source.id,
        )
    )

    if existing:
        print("Mapping already exists:")
        print("Manga:", manga.title)
        print("Source:", source.name)
        print("Source Manga ID:", existing.source_manga_id)
        print("URL:", existing.source_url)
    else:
        mapping = MangaSourceMapping(
            manga_id=manga.id,
            source_id=source.id,
            source_manga_id="247fe684-e74b-42f9-ae63-0c410a663408",
            source_title="Magic Kaito",
            source_url=(
                "https://mangadex.org/title/"
                "247fe684-e74b-42f9-ae63-0c410a663408"
            ),
        )

        db.add(mapping)
        db.commit()

        print("Mapping created:")
        print("Manga:", manga.title)
        print("Source:", source.name)
        print("Source Manga ID:", mapping.source_manga_id)
        print("URL:", mapping.source_url)