from datetime import date

from pydantic import BaseModel, ConfigDict

from app.models import Gender, RelationType


class PersonBase(BaseModel):
    name: str
    gender: Gender = Gender.unknown
    birth_date: date | None = None
    death_date: date | None = None
    photo_url: str | None = None


class PersonCreate(PersonBase):
    pass


class PersonUpdate(PersonBase):
    pass


class PersonRead(PersonBase):
    model_config = ConfigDict(from_attributes=True)

    id: int


class RelationshipBase(BaseModel):
    type: RelationType
    person_a_id: int
    person_b_id: int


class RelationshipCreate(RelationshipBase):
    pass


class RelationshipRead(RelationshipBase):
    model_config = ConfigDict(from_attributes=True)

    id: int


class GraphNode(BaseModel):
    id: str
    data: PersonRead


class GraphEdge(BaseModel):
    id: str
    source: str
    target: str
    type: RelationType


class GraphResponse(BaseModel):
    nodes: list[GraphNode]
    edges: list[GraphEdge]


class RelativesResponse(BaseModel):
    parents: list[PersonRead]
    children: list[PersonRead]
    spouses: list[PersonRead]
    siblings: list[PersonRead]
    ancestors: list[PersonRead]
    descendants: list[PersonRead]
    cousins: list[PersonRead]


class KinshipTermRead(BaseModel):
    person: PersonRead
    term: str
