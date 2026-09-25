from sqlalchemy import func, select

from app.database import SessionLocal
from app.models import Manga, Source, Chapter, ChapterSource


with SessionLocal() as db:

    manga_count = db.scalar(
        select(func.count()).select_from(Manga)
    )

    source_count = db.scalar(
        select(func.count()).select_from(Source)
    )

    chapter_count = db.scalar(
        select(func.count()).select_from(Chapter)
    )

    chapter_source_count = db.scalar(
        select(func.count()).select_from(ChapterSource)
    )

    print("MANGA:", manga_count)
    print("SOURCES:", source_count)
    print("CANONICAL CHAPTERS:", chapter_count)
    print("SOURCE CHAPTERS:", chapter_source_count)

    print("\nCHAPTER 1154:")

    chapter = db.scalar(
        select(Chapter).where(
            Chapter.chapter_number == "1154"
        )
    )

    if chapter:
        print(
            f"Canonical chapter ID: {chapter.id}"
        )
        print(
            f"Chapter number: {chapter.chapter_number}"
        )
        print(
            f"Title: {chapter.title}"
        )

        for source_chapter in chapter.source_chapters:
            print(
                f"  Source: {source_chapter.source.key}"
            )
            print(
                f"  Source chapter ID: "
                f"{source_chapter.source_chapter_id}"
            )
            print(
                f"  URL: {source_chapter.url}"
            )
            print()