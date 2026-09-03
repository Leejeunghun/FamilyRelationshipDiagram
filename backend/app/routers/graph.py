from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import crud, schemas
from app.database import get_db
from app.deps import get_owner_id
from app.relationships import FamilyGraph

router = APIRouter(tags=["graph"])


@router.get("/graph", response_model=schemas.GraphResponse)
def get_graph(db: Session = Depends(get_db), owner_id: str = Depends(get_owner_id)):
    graph = FamilyGraph(db, owner_id)
    nodes, edges = graph.to_graph_payload()
    return {"nodes": nodes, "edges": edges}


@router.get("/people/{person_id}/relatives", response_model=schemas.RelativesResponse)
def get_relatives(person_id: int, db: Session = Depends(get_db), owner_id: str = Depends(get_owner_id)):
    if crud.get_person(db, owner_id, person_id) is None:
        raise HTTPException(status_code=404, detail="Person not found")
    graph = FamilyGraph(db, owner_id)
    return {
        "parents": graph.parents(person_id),
        "children": graph.children(person_id),
        "spouses": graph.spouses(person_id),
        "siblings": graph.siblings(person_id),
        "ancestors": graph.ancestors(person_id),
        "descendants": graph.descendants(person_id),
        "cousins": graph.cousins(person_id),
    }
