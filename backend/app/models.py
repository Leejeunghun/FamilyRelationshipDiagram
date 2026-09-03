import enum

from sqlalchemy import Date, Enum, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Gender(str, enum.Enum):
    male = "male"
    female = "female"
    unknown = "unknown"


class RelationType(str, enum.Enum):
    parent_child = "parent_child"
    spouse = "spouse"


class Person(Base):
    __tablename__ = "people"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    gender: Mapped[Gender] = mapped_column(Enum(Gender), default=Gender.unknown, nullable=False)
    birth_date: Mapped[str | None] = mapped_column(Date, nullable=True)
    death_date: Mapped[str | None] = mapped_column(Date, nullable=True)
    photo_url: Mapped[str | None] = mapped_column(String(500), nullable=True)


class Relationship(Base):
    __tablename__ = "relationships"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    type: Mapped[RelationType] = mapped_column(Enum(RelationType), nullable=False)
    # parent_child: person_a = 부모, person_b = 자녀
    # spouse: 순서 무관
    person_a_id: Mapped[int] = mapped_column(ForeignKey("people.id", ondelete="CASCADE"), nullable=False)
    person_b_id: Mapped[int] = mapped_column(ForeignKey("people.id", ondelete="CASCADE"), nullable=False)

    person_a: Mapped["Person"] = relationship(foreign_keys=[person_a_id])
    person_b: Mapped["Person"] = relationship(foreign_keys=[person_b_id])
