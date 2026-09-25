from sqlalchemy import select

from ..database import SessionLocal
from ..models import Manga, Source, Chapter, ChapterSource
from ..sources.base import MangaSource


async def sync_manga_source(
    manga_id: int,
    source: MangaSource,
    source_manga,
) -> dict:

    with SessionLocal() as db:

        # Make sure the source exists in our database.
        db_source = db.scalar(
            select(Source).where(
                Source.key == source.key
            )
        )

        if db_source is None:
            db_source = Source(
                key=source.key,
                name=source.name,
            )

            db.add(db_source)
            db.flush()

        # Make sure the MangaAsari manga exists.
        manga = db.get(Manga, manga_id)

        if manga is None:
            raise ValueError(
                f"Manga with ID {manga_id} does not exist"
            )

        # Get chapters from the external source.
        source_chapters = await source.get_chapters(
            source_manga
        )

        created_chapters = 0
        created_source_chapters = 0

        for source_chapter in source_chapters:

            # Find the canonical MangaAsari chapter.
            chapter = db.scalar(
                select(Chapter).where(
                    Chapter.manga_id == manga.id,
                    Chapter.chapter_number
                    == source_chapter.chapter_number,
                )
            )

            if chapter is None:
                chapter = Chapter(
                    manga_id=manga.id,
                    chapter_number=source_chapter.chapter_number,
                    title=source_chapter.title,
                )

                db.add(chapter)
                db.flush()

                created_chapters += 1

            # Check whether this exact source chapter
            # has already been stored.
            existing_source_chapter = db.scalar(
                select(ChapterSource).where(
                    ChapterSource.source_id == db_source.id,
                    ChapterSource.source_chapter_id
                    == source_chapter.source_chapter_id,
                )
            )

            if existing_source_chapter is None:

                chapter_source = ChapterSource(
                    chapter_id=chapter.id,
                    source_id=db_source.id,
                    source_chapter_id=(
                        source_chapter.source_chapter_id
                    ),
                    manga_source_id=(
                        source_chapter.manga_source_id
                    ),
                    url=source_chapter.url,
                    language="en",
                )

                db.add(chapter_source)

                created_source_chapters += 1

        db.commit()

        return {
            "source": source.key,
            "chapters_found": len(source_chapters),
            "chapters_created": created_chapters,
            "source_chapters_created": (
                created_source_chapters
            ),
        }