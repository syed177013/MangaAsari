from .base import MangaSource, SourceChapter, SourceManga


class MockSource(MangaSource):

    key = "mock"
    name = "Mock Source"

    async def search(self, title: str) -> list[SourceManga]:
        return [
            SourceManga(
                source_id="detective-conan",
                title="Detective Conan",
                url="https://example.com/detective-conan",
            )
        ]

    async def get_chapters(
        self,
        manga: SourceManga,
    ) -> list[SourceChapter]:

        return [
            SourceChapter(
                source_id=self.key,
                manga_source_id=manga.source_id,
                source_chapter_id="mock-1170",
                chapter_number="1170",
                title="Example Chapter",
                url="https://example.com/detective-conan/1170",
            ),
            SourceChapter(
                source_id=self.key,
                manga_source_id=manga.source_id,
                source_chapter_id="mock-1169",
                chapter_number="1169",
                title=None,
                url="https://example.com/detective-conan/1169",
            ),
        ]