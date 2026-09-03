from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import crud, schemas
from app.database import get_db
from app.deps import get_owner_id

router = APIRouter(prefix="/relationships", tags=["relationships"])


@router.get("", response_model=list[schemas.RelationshipRead])
def list_relationships(db: Session = Depends(get_db), owner_id: str = Depends(get_owner_id)):
    return crud.get_relationships(db, owner_id)


@router.post("", response_model=schemas.RelationshipRead, status_code=201)
def create_relationship(
    rel: schemas.RelationshipCreate, db: Session = Depends(get_db), owner_id: str = Depends(get_owner_id)
):
    if rel.person_a_id == rel.person_b_id:
        raise HTTPException(status_code=400, detail="같은 사람끼리는 관계를 맺을 수 없습니다")
    # get_person이 owner_id로도 필터링하므로, 두 사람 모두 같은 소유자여야만 통과한다.
    if crud.get_person(db, owner_id, rel.person_a_id) is None or crud.get_person(db, owner_id, rel.person_b_id) is None:
        raise HTTPException(status_code=404, detail="Person not found")
    if crud.find_duplicate_relationship(db, owner_id, rel) is not None:
        raise HTTPException(status_code=409, detail="이미 존재하는 관계입니다")
    return crud.create_relationship(db, owner_id, rel)


@router.delete("/{relationship_id}", status_code=204)
def delete_relationship(relationship_id: int, db: Session = Depends(get_db), owner_id: str = Depends(get_owner_id)):
    if not crud.delete_relationship(db, owner_id, relationship_id):
        raise HTTPException(status_code=404, detail="Relationship not found")
