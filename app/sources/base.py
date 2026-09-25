from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class SourceManga:
    source_id: str
    title: str
    url: str


@dataclass
class SourceChapter:
    source_id: str
    manga_source_id: str
    source_chapter_id: str
    chapter_number: str
    title: str | None
    url: str


class MangaSource(ABC):

    key: str
    name: str

    @abstractmethod
    async def search(self, title: str) -> list[SourceManga]:
        """Search this source for a manga."""
        raise NotImplementedError

    @abstractmethod
    async def get_chapters(
        self,
        manga: SourceManga,
    ) -> list[SourceChapter]:
        """Return chapters for a source manga."""
        raise NotImplementedError