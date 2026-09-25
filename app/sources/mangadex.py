import httpx

from .base import MangaSource, SourceManga, SourceChapter


MANGADEX_API = "https://api.mangadex.org"


class MangaDexSource(MangaSource):

    key = "mangadex"
    name = "MangaDex"

    async def search(self, title: str) -> list[SourceManga]:

        params = {
            "title": title,
            "limit": 10,
        }

        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                f"{MANGADEX_API}/manga",
                params=params,
            )

        response.raise_for_status()

        data = response.json()

        results = []

        for item in data.get("data", []):

            manga_id = item["id"]
            attributes = item["attributes"]

            titles = attributes.get("title", {})

            manga_title = (
                titles.get("en")
                or titles.get("ja-ro")
                or next(iter(titles.values()), "Unknown")
            )

            results.append(
                SourceManga(
                    source_id=manga_id,
                    title=manga_title,
                    url=f"https://mangadex.org/title/{manga_id}",
                )
            )

        return results

    async def get_chapters(
        self,
        manga: SourceManga,
    ) -> list[SourceChapter]:

        limit = 100
        offset = 0

        chapters = []

        async with httpx.AsyncClient(timeout=10.0) as client:

            while True:

                params = {
                    "limit": limit,
                    "offset": offset,
                    "translatedLanguage[]": "en",
                    "order[chapter]": "desc",
                }

                response = await client.get(
                    f"{MANGADEX_API}/manga/{manga.source_id}/feed",
                    params=params,
                )

                if response.status_code != 200:
                    print("MangaDex response:")
                    print(response.text)

                response.raise_for_status()

                data = response.json()

                page_data = data.get("data", [])
                total = data.get("total", 0)

                print(
                    f"Fetched {len(page_data)} chapters "
                    f"(offset={offset}, total={total})"
                )

                for item in page_data:

                    chapter_id = item["id"]
                    attributes = item["attributes"]

                    chapter_number = attributes.get("chapter")

                    if chapter_number is None:
                        continue

                    chapters.append(
                        SourceChapter(
                            source_id=self.key,
                            manga_source_id=manga.source_id,
                            source_chapter_id=chapter_id,
                            chapter_number=chapter_number,
                            title=attributes.get("title"),
                            url=f"https://mangadex.org/chapter/{chapter_id}",
                        )
                    )

                offset += len(page_data)

                if not page_data or offset >= total:
                    break

        return chapters