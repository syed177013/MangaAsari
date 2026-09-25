import httpx


ANILIST_URL = "https://graphql.anilist.co"


async def search_manga(search: str) -> list[dict]:
    query = """
    query ($search: String) {
        Page(perPage: 10) {
            media(
                search: $search
                type: MANGA
            ) {
                id
                title {
                    romaji
                    english
                    native
                }
                synonyms
                coverImage {
                    medium
                }
                chapters
                volumes
                status
            }
        }
    }
    """

    variables = {
        "search": search,
    }

    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.post(
            ANILIST_URL,
            json={
                "query": query,
                "variables": variables,
            },
        )

    response.raise_for_status()

    data = response.json()

    if "errors" in data:
        raise RuntimeError(data["errors"])

    return data["data"]["Page"]["media"]