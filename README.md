# MangaAsari


MangaAsari is a small manga discovery and chapter aggregation project.

Right now it uses **AniList** for manga search and the **MangaDex API** to find and fetch available chapters in a preset language. Pick a chapter and MangaAsari sends you straight to the original MangaDex reader.

No reader of its own yet. No scraping. Just API → database → link.

## Why?

Mostly because I got tired of digging through manga sites to find a specific chapter.

The other reason is that this is a playground for experimenting with APIs, databases, backend development, and eventually Android.

The bigger idea is to have multiple manga sources behind one interface instead of building the whole application around one site's API.

---

## How it works

```text
User
 │
 ├── Search manga
 │       ↓
 │    AniList
 │       ↓
 │   MangaAsari DB
 │       ↓
 ├── Find source
 │       ↓
 │    MangaDex API
 │       ↓
 │   Chapter metadata
 │       ↓
 │   MangaAsari DB
 │       ↓
 └── Pick chapter
         ↓
   Original MangaDex URL
```

MangaAsari keeps its own local representation of the data instead of storing raw API responses.

The important distinction is between **a manga/chapter itself** and **where that manga/chapter exists on a particular source**.

---

## Database

SQLite + SQLAlchemy.

The current schema is basically:

```text
Manga
  │
  ├── MangaSourceMapping ──→ Source
  │
  └── Chapter
        │
        └── ChapterSource ──→ Source
```

### `Manga`

The canonical manga in MangaAsari.

It stores things such as the AniList ID, titles, cover and status.

### `Source`

An external manga source.

Currently:

```text
mangadex → MangaDex
```

### `MangaSourceMapping`

Maps a MangaAsari manga to its ID on a particular source.

For example:

```text
Detective Conan
      ↓
MangaDex
      ↓
7f30dfc3-0b80-4dcc-a3b9-0cd746fac005
```

This means we don't have to search the source every time we synchronize.

### `Chapter`

The canonical chapter inside MangaAsari.

### `ChapterSource`

The source-specific version of a chapter.

This is important because two sources can have the same chapter, and even the same source can have multiple releases of a chapter.

So:

```text
Chapter 1154
   ├── MangaDex release A
   ├── MangaDex release B
   └── Another source
```

can all exist without creating three different canonical chapters.

---

## MangaDex API

MangaDex is currently the first implemented source.

The integration lives under:

```text
app/
└── sources/
    ├── base.py
    ├── mock.py
    └── mangadex.py
```

`base.py` defines the interface:

```python
class MangaSource:
    async def search(title):
        ...

    async def get_chapters(manga):
        ...
```

`mangadex.py` implements it for MangaDex.

That's intentional. Adding another source should mean implementing the same interface rather than rewriting the application.

---

## Chapter Sync

Synchronization is designed to be idempotent.

On sync, MangaAsari:

1. Fetches the source's chapters.
2. Finds or creates the canonical chapter.
3. Finds or creates the source-specific chapter record.
4. Saves the changes.

Running the same sync again doesn't create duplicates.

For example, a Detective Conan MangaDex feed returned **1,558 source chapter records**, which resulted in **1,168 canonical chapters** because multiple source releases can have the same chapter number.

Running the sync again added **0 new chapters**.

---

## Current Features

* AniList manga search
* Local manga library
* MangaDex source search
* Manual source matching
* Source-to-manga mapping
* Chapter synchronization
* SQLite database
* Multiple source releases per chapter
* Direct links to MangaDex chapters
* Idempotent synchronization
* Source abstraction for future integrations

---

## Running Locally

Requires **Python 3.11+**.

```powershell
git clone <YOUR-REPOSITORY-URL>
cd MangaAsari

python -m venv .venv
.venv\Scripts\Activate.ps1

pip install -r requirements.txt

uvicorn app.main:app --reload
```

Then open:

```text
http://127.0.0.1:8000
```

That's it.

---

## Roadmap

Stuff I'd like to mess with if I get around to it:

* [ ] Add more sources
* [ ] Better source matching
* [ ] Sleeker UI
* [ ] User-selectable languages
* [ ] Better chapter filtering/sorting
* [ ] Reading progress
* [ ] Chapter notifications
* [ ] Local reader
* [ ] Android app

The Android app is mostly an excuse to learn and experiment.

---

## Third-Party Services

* **[MangaDex](https://mangadex.org/)** — source search and chapter metadata
* **[AniList](https://anilist.co/)** — manga search and metadata

MangaAsari is not affiliated with or endorsed by either service.

MangaAsari currently does not host or redistribute manga content. Chapter links point back to the original source.

MangaDex's API has its own usage requirements and policies. If this project is expanded into an in-app reader or otherwise changes how MangaDex content is used, those requirements will need to be reviewed again.

**MangaDex API documentation:**
https://api.mangadex.org/docs/

---

## License

The MangaAsari source code is licensed under the **MIT License**.

The license applies to this project's code only. It does not grant rights to third-party APIs, manga, artwork, trademarks, or other content accessed through them.

See [`LICENSE`](LICENSE) for the full license text.

---

## Author

**Syed Mustafa Ahmed**

Built because apparently making a manga aggregator is more fun than making another todo app.
