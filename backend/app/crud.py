from sqlalchemy import or_
from sqlalchemy.orm import Session

from app import models, schemas


def get_people(db: Session, owner_id: str) -> list[models.Person]:
    return db.query(models.Person).filter(models.Person.owner_id == owner_id).order_by(models.Person.id).all()


def get_person(db: Session, owner_id: str, person_id: int) -> models.Person | None:
    return (
        db.query(models.Person)
        .filter(models.Person.id == person_id, models.Person.owner_id == owner_id)
        .first()
    )


def create_person(db: Session, owner_id: str, person: schemas.PersonCreate) -> models.Person:
    db_person = models.Person(owner_id=owner_id, **person.model_dump())
    db.add(db_person)
    db.commit()
    db.refresh(db_person)
    return db_person


def update_person(db: Session, owner_id: str, person_id: int, person: schemas.PersonUpdate) -> models.Person | None:
    db_person = get_person(db, owner_id, person_id)
    if db_person is None:
        return None
    for key, value in person.model_dump().items():
        setattr(db_person, key, value)
    db.commit()
    db.refresh(db_person)
    return db_person


def delete_person(db: Session, owner_id: str, person_id: int) -> bool:
    db_person = get_person(db, owner_id, person_id)
    if db_person is None:
        return False
    db.query(models.Relationship).filter(
        models.Relationship.owner_id == owner_id,
        or_(
            models.Relationship.person_a_id == person_id,
            models.Relationship.person_b_id == person_id,
        ),
    ).delete()
    db.delete(db_person)
    db.commit()
    return True


def get_relationships(db: Session, owner_id: str) -> list[models.Relationship]:
    return (
        db.query(models.Relationship)
        .filter(models.Relationship.owner_id == owner_id)
        .order_by(models.Relationship.id)
        .all()
    )


def get_relationship(db: Session, owner_id: str, relationship_id: int) -> models.Relationship | None:
    return (
        db.query(models.Relationship)
        .filter(models.Relationship.id == relationship_id, models.Relationship.owner_id == owner_id)
        .first()
    )


def find_duplicate_relationship(
    db: Session, owner_id: str, rel: schemas.RelationshipCreate
) -> models.Relationship | None:
    query = db.query(models.Relationship).filter(
        models.Relationship.owner_id == owner_id, models.Relationship.type == rel.type
    )
    if rel.type == models.RelationType.spouse:
        query = query.filter(
            or_(
                (models.Relationship.person_a_id == rel.person_a_id)
                & (models.Relationship.person_b_id == rel.person_b_id),
                (models.Relationship.person_a_id == rel.person_b_id)
                & (models.Relationship.person_b_id == rel.person_a_id),
            )
        )
    else:
        query = query.filter(
            models.Relationship.person_a_id == rel.person_a_id,
            models.Relationship.person_b_id == rel.person_b_id,
        )
    return query.first()


def create_relationship(db: Session, owner_id: str, rel: schemas.RelationshipCreate) -> models.Relationship:
    db_rel = models.Relationship(owner_id=owner_id, **rel.model_dump())
    db.add(db_rel)
    db.commit()
    db.refresh(db_rel)
    return db_rel


def delete_relationship(db: Session, owner_id: str, relationship_id: int) -> bool:
    db_rel = get_relationship(db, owner_id, relationship_id)
    if db_rel is None:
        return False
    db.delete(db_rel)
    db.commit()
    return True
