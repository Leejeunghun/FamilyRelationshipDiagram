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
    # 로그인 없이 브라우저별 익명 ID로 가족관계도를 분리하기 위한 소유자 식별자.
    # 인증이 아니라 단순 구분값이므로, 값을 아는 사람은 누구나 접근 가능하다는 한계가 있다.
    owner_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    gender: Mapped[Gender] = mapped_column(Enum(Gender), default=Gender.unknown, nullable=False)
    birth_date: Mapped[str | None] = mapped_column(Date, nullable=True)
    death_date: Mapped[str | None] = mapped_column(Date, nullable=True)
    photo_url: Mapped[str | None] = mapped_column(String(500), nullable=True)


class Relationship(Base):
    __tablename__ = "relationships"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    owner_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    type: Mapped[RelationType] = mapped_column(Enum(RelationType), nullable=False)
    # parent_child: person_a = 부모, person_b = 자녀
    # spouse: 순서 무관
    person_a_id: Mapped[int] = mapped_column(ForeignKey("people.id", ondelete="CASCADE"), nullable=False)
    person_b_id: Mapped[int] = mapped_column(ForeignKey("people.id", ondelete="CASCADE"), nullable=False)

    person_a: Mapped["Person"] = relationship(foreign_keys=[person_a_id])
    person_b: Mapped["Person"] = relationship(foreign_keys=[person_b_id])
