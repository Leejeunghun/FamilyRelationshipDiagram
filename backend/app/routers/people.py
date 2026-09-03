from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import crud, schemas
from app.database import get_db
from app.deps import get_owner_id

router = APIRouter(prefix="/people", tags=["people"])


@router.get("", response_model=list[schemas.PersonRead])
def list_people(db: Session = Depends(get_db), owner_id: str = Depends(get_owner_id)):
    return crud.get_people(db, owner_id)


@router.post("", response_model=schemas.PersonRead, status_code=201)
def create_person(person: schemas.PersonCreate, db: Session = Depends(get_db), owner_id: str = Depends(get_owner_id)):
    return crud.create_person(db, owner_id, person)


@router.get("/{person_id}", response_model=schemas.PersonRead)
def get_person(person_id: int, db: Session = Depends(get_db), owner_id: str = Depends(get_owner_id)):
    person = crud.get_person(db, owner_id, person_id)
    if person is None:
        raise HTTPException(status_code=404, detail="Person not found")
    return person


@router.put("/{person_id}", response_model=schemas.PersonRead)
def update_person(
    person_id: int,
    person: schemas.PersonUpdate,
    db: Session = Depends(get_db),
    owner_id: str = Depends(get_owner_id),
):
    updated = crud.update_person(db, owner_id, person_id, person)
    if updated is None:
        raise HTTPException(status_code=404, detail="Person not found")
    return updated


@router.delete("/{person_id}", status_code=204)
def delete_person(person_id: int, db: Session = Depends(get_db), owner_id: str = Depends(get_owner_id)):
    if not crud.delete_person(db, owner_id, person_id):
        raise HTTPException(status_code=404, detail="Person not found")
