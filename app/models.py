from sqlalchemy import ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base


class Manga(Base):
    __tablename__ = "manga"

    id: Mapped[int] = mapped_column(primary_key=True)

    # Stable identity from AniList
    anilist_id: Mapped[int] = mapped_column(
        unique=True,
        index=True,
    )

    title: Mapped[str] = mapped_column(
        String(255),
    )

    romaji_title: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    native_title: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    aliases: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    cover_url: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )

    status: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    chapters: Mapped[list["Chapter"]] = relationship(
        back_populates="manga",
        cascade="all, delete-orphan",
    )
    source_mappings: Mapped[list["MangaSourceMapping"]] = relationship(
    back_populates="manga",
    cascade="all, delete-orphan",
    )



class Source(Base):
    __tablename__ = "source"

    id: Mapped[int] = mapped_column(
        primary_key=True,
    )

    key: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        index=True,
    )

    name: Mapped[str] = mapped_column(
        String(100),
    )

    base_url: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )

    enabled: Mapped[bool] = mapped_column(
        default=True,
    )

    chapter_sources: Mapped[list["ChapterSource"]] = relationship(
        back_populates="source",
        cascade="all, delete-orphan",
    )
    manga_mappings: Mapped[list["MangaSourceMapping"]] = relationship(
    back_populates="source",
    cascade="all, delete-orphan",
    )


class Chapter(Base):
    __tablename__ = "chapter"

    id: Mapped[int] = mapped_column(
        primary_key=True,
    )

    manga_id: Mapped[int] = mapped_column(
        ForeignKey("manga.id"),
        index=True,
    )

    # Stored as text because chapters can be:
    # 12, 12.5, 0.5, Extra, Prologue, etc.
    chapter_number: Mapped[str] = mapped_column(
        String(50),
    )

    title: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    manga: Mapped["Manga"] = relationship(
        back_populates="chapters",
    )

    source_chapters: Mapped[list["ChapterSource"]] = relationship(
        back_populates="chapter",
        cascade="all, delete-orphan",
    )

    __table_args__ = (
        UniqueConstraint(
            "manga_id",
            "chapter_number",
            name="uq_manga_chapter_number",
        ),
    )


class ChapterSource(Base):
    __tablename__ = "chapter_source"

    id: Mapped[int] = mapped_column(
        primary_key=True,
    )

    chapter_id: Mapped[int] = mapped_column(
        ForeignKey("chapter.id"),
        index=True,
    )

    source_id: Mapped[int] = mapped_column(
        ForeignKey("source.id"),
        index=True,
    )

    # The chapter's ID on the external source.
    source_chapter_id: Mapped[str] = mapped_column(
        String(255),
    )

    # The manga's ID on the external source.
    manga_source_id: Mapped[str] = mapped_column(
        String(255),
    )

    url: Mapped[str] = mapped_column(
        String(1000),
    )

    language: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
    )

    group_name: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    is_available: Mapped[bool] = mapped_column(
        default=True,
    )

    chapter: Mapped["Chapter"] = relationship(
        back_populates="source_chapters",
    )

    source: Mapped["Source"] = relationship(
        back_populates="chapter_sources",
    )

    __table_args__ = (
        UniqueConstraint(
            "source_id",
            "source_chapter_id",
            name="uq_source_chapter",
        ),
    )

class MangaSourceMapping(Base):
    __tablename__ = "manga_source_mapping"

    id: Mapped[int] = mapped_column(primary_key=True)

    manga_id: Mapped[int] = mapped_column(
        ForeignKey("manga.id"),
        index=True,
    )

    source_id: Mapped[int] = mapped_column(
        ForeignKey("source.id"),
        index=True,
    )

    source_manga_id: Mapped[str] = mapped_column(
        String(255)
    )

    source_title: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    source_url: Mapped[str | None] = mapped_column(
        String(1000),
        nullable=True,
    )

    enabled: Mapped[bool] = mapped_column(
        default=True
    )

    manga: Mapped["Manga"] = relationship(
        back_populates="source_mappings"
    )

    source: Mapped["Source"] = relationship(
        back_populates="manga_mappings"
    )

    __table_args__ = (
        UniqueConstraint(
            "manga_id",
            "source_id",
            name="uq_manga_source_mapping",
        ),
    )