from .sources.base import SourceManga
from .services.sync import sync_manga_source
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import select

from .anilist import search_manga
from .database import Base, SessionLocal, engine
from .models import Manga, Chapter, Source, MangaSourceMapping
from .sources.mangadex import MangaDexSource


Base.metadata.create_all(bind=engine)

app = FastAPI(title="MangaAsari")

templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"title": "MangaAsari"},
    )


@app.get("/api/search")
async def api_search_manga(q: str):

    if not q.strip():
        return {"results": []}

    results = await search_manga(q.strip())

    return {
        "results": results,
    }


@app.post("/api/library")
async def add_to_library(manga_data: dict):

    anilist_id = manga_data.get("anilist_id")

    if not anilist_id:
        raise HTTPException(
            status_code=400,
            detail="Missing AniList ID",
        )

    with SessionLocal() as db:

        existing = db.scalar(
            select(Manga).where(
                Manga.anilist_id == anilist_id
            )
        )

        if existing:
            return {
                "message": "Manga already in library",
                "id": existing.id,
            }

        manga = Manga(
            anilist_id=anilist_id,
            title=manga_data.get(
                "title",
                "Unknown",
            ),
            romaji_title=manga_data.get(
                "romaji_title"
            ),
            native_title=manga_data.get(
                "native_title"
            ),
            aliases=manga_data.get(
                "aliases"
            ),
            cover_url=manga_data.get(
                "cover_url"
            ),
            status=manga_data.get(
                "status"
            ),
        )

        db.add(manga)
        db.commit()
        db.refresh(manga)

        return {
            "message": "Manga added",
            "id": manga.id,
        }


@app.get("/api/library")
async def get_library():

    with SessionLocal() as db:

        manga_list = db.scalars(
            select(Manga).order_by(Manga.title)
        ).all()

        return {
            "manga": [
                {
                    "id": manga.id,
                    "anilist_id": manga.anilist_id,
                    "title": manga.title,
                    "romaji_title": manga.romaji_title,
                    "native_title": manga.native_title,
                    "cover_url": manga.cover_url,
                    "status": manga.status,
                }
                for manga in manga_list
            ]
        }


@app.get("/api/library/{manga_id}/chapters")
async def get_manga_chapters(manga_id: int):

    with SessionLocal() as db:

        manga = db.get(Manga, manga_id)

        if manga is None:
            raise HTTPException(
                status_code=404,
                detail="Manga not found",
            )

        chapters = db.scalars(
            select(Chapter)
            .where(Chapter.manga_id == manga.id)
            .order_by(Chapter.id.desc())
        ).all()

        return {
            "manga": {
                "id": manga.id,
                "title": manga.title,
            },
            "chapters": [
                {
                    "id": chapter.id,
                    "number": chapter.chapter_number,
                    "title": chapter.title,
                    "sources": [
                        {
                            "source": source_chapter.source.key,
                            "source_name": source_chapter.source.name,
                            "source_chapter_id": (
                                source_chapter.source_chapter_id
                            ),
                            "url": source_chapter.url,
                        }
                        for source_chapter
                        in chapter.source_chapters
                    ],
                }
                for chapter in chapters
            ],
        }

@app.get("/api/library/{manga_id}/source-search")
async def search_manga_source(manga_id: int):

    with SessionLocal() as db:

        manga = db.get(Manga, manga_id)

        if manga is None:
            raise HTTPException(
                status_code=404,
                detail="Manga not found",
            )

        title = (
            manga.romaji_title
            or manga.title
        )

    source = MangaDexSource()

    results = await source.search(title)

    return {
        "manga": {
            "id": manga_id,
            "title": manga.title,
        },
        "source": source.key,
        "source_name": source.name,
        "results": [
            {
                "source_id": result.source_id,
                "title": result.title,
                "url": result.url,
            }
            for result in results
        ],
    }

@app.post("/api/library/{manga_id}/sources/mangadex")
async def save_mangadex_mapping(
    manga_id: int,
    source_manga_id: str,
    source_title: str,
    source_url: str,
):
    with SessionLocal() as db:
        manga = db.get(Manga, manga_id)

        if manga is None:
            raise HTTPException(
                status_code=404,
                detail="Manga not found",
            )

        source = db.scalar(
            select(Source).where(Source.key == "mangadex")
        )

        if source is None:
            source = Source(
                key="mangadex",
                name="MangaDex",
                base_url="https://mangadex.org",
            )
            db.add(source)
            db.flush()

        mapping = db.scalar(
            select(MangaSourceMapping).where(
                MangaSourceMapping.manga_id == manga.id,
                MangaSourceMapping.source_id == source.id,
            )
        )

        if mapping is None:
            mapping = MangaSourceMapping(
                manga_id=manga.id,
                source_id=source.id,
                source_manga_id=source_manga_id,
                source_title=source_title,
                source_url=source_url,
            )
            db.add(mapping)
            message = "Source mapping created"
        else:
            mapping.source_manga_id = source_manga_id
            mapping.source_title = source_title
            mapping.source_url = source_url
            mapping.enabled = True
            message = "Source mapping updated"

        db.commit()
        db.refresh(mapping)

        return {
            "message": message,
            "mapping": {
                "id": mapping.id,
                "manga_id": mapping.manga_id,
                "source": source.key,
                "source_name": source.name,
                "source_manga_id": mapping.source_manga_id,
                "source_title": mapping.source_title,
                "source_url": mapping.source_url,
                "enabled": mapping.enabled,
            },
        }

@app.post("/api/library/{manga_id}/sync/mangadex")
async def sync_manga_from_mangadex(manga_id: int):
    with SessionLocal() as db:
        manga = db.get(Manga, manga_id)

        if manga is None:
            raise HTTPException(
                status_code=404,
                detail="Manga not found",
            )

        source = db.scalar(
            select(Source).where(Source.key == "mangadex")
        )

        if source is None:
            raise HTTPException(
                status_code=404,
                detail="MangaDex source not found",
            )

        mapping = db.scalar(
            select(MangaSourceMapping).where(
                MangaSourceMapping.manga_id == manga.id,
                MangaSourceMapping.source_id == source.id,
                MangaSourceMapping.enabled.is_(True),
            )
        )

        if mapping is None:
            raise HTTPException(
                status_code=404,
                detail="No MangaDex source mapping found",
            )

        source_manga = SourceManga(
            source_id=mapping.source_manga_id,
            title=mapping.source_title or manga.title,
            url=mapping.source_url or (
                "https://mangadex.org/title/"
                f"{mapping.source_manga_id}"
            ),
        )

    result = await sync_manga_source(
        manga_id=manga_id,
        source=MangaDexSource(),
        source_manga=source_manga,
    )

    return result