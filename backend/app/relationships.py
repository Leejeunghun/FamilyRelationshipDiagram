"""parent-child / spouse 두 종류의 저장된 관계만으로 형제/조상/자손/사촌 등을 계산한다."""

from collections import defaultdict

from sqlalchemy.orm import Session

from app import crud, models


class FamilyGraph:
    """전체 Person/Relationship을 한 번 읽어 메모리 상의 인접 리스트로 구성."""

    def __init__(self, db: Session):
        self.people: dict[int, models.Person] = {p.id: p for p in crud.get_people(db)}
        self.parents_of: dict[int, set[int]] = defaultdict(set)
        self.children_of: dict[int, set[int]] = defaultdict(set)
        self.spouses_of: dict[int, set[int]] = defaultdict(set)

        for rel in crud.get_relationships(db):
            if rel.type == models.RelationType.parent_child:
                self.parents_of[rel.person_b_id].add(rel.person_a_id)
                self.children_of[rel.person_a_id].add(rel.person_b_id)
            elif rel.type == models.RelationType.spouse:
                self.spouses_of[rel.person_a_id].add(rel.person_b_id)
                self.spouses_of[rel.person_b_id].add(rel.person_a_id)

    def _resolve(self, ids: set[int]) -> list[models.Person]:
        return [self.people[i] for i in sorted(ids) if i in self.people]

    def parents(self, person_id: int) -> list[models.Person]:
        return self._resolve(self.parents_of.get(person_id, set()))

    def children(self, person_id: int) -> list[models.Person]:
        return self._resolve(self.children_of.get(person_id, set()))

    def spouses(self, person_id: int) -> list[models.Person]:
        return self._resolve(self.spouses_of.get(person_id, set()))

    def siblings(self, person_id: int) -> list[models.Person]:
        """부모를 하나라도 공유하는 사람들 (본인 제외)."""
        result: set[int] = set()
        for parent_id in self.parents_of.get(person_id, set()):
            result |= self.children_of.get(parent_id, set())
        result.discard(person_id)
        return self._resolve(result)

    def ancestors(self, person_id: int, max_depth: int = 10) -> list[models.Person]:
        visited: set[int] = set()
        frontier = {person_id}
        for _ in range(max_depth):
            next_frontier: set[int] = set()
            for pid in frontier:
                next_frontier |= self.parents_of.get(pid, set())
            next_frontier -= visited
            next_frontier.discard(person_id)
            if not next_frontier:
                break
            visited |= next_frontier
            frontier = next_frontier
        return self._resolve(visited)

    def descendants(self, person_id: int, max_depth: int = 10) -> list[models.Person]:
        visited: set[int] = set()
        frontier = {person_id}
        for _ in range(max_depth):
            next_frontier: set[int] = set()
            for pid in frontier:
                next_frontier |= self.children_of.get(pid, set())
            next_frontier -= visited
            next_frontier.discard(person_id)
            if not next_frontier:
                break
            visited |= next_frontier
            frontier = next_frontier
        return self._resolve(visited)

    def cousins(self, person_id: int) -> list[models.Person]:
        """부모의 형제자매의 자녀들."""
        result: set[int] = set()
        for parent_id in self.parents_of.get(person_id, set()):
            for aunt_uncle_id in self.siblings_ids(parent_id):
                result |= self.children_of.get(aunt_uncle_id, set())
        return self._resolve(result)

    def siblings_ids(self, person_id: int) -> set[int]:
        result: set[int] = set()
        for parent_id in self.parents_of.get(person_id, set()):
            result |= self.children_of.get(parent_id, set())
        result.discard(person_id)
        return result

    def to_graph_payload(self) -> tuple[list[dict], list[dict]]:
        nodes = [{"id": str(pid), "data": person} for pid, person in self.people.items()]
        edges: list[dict] = []
        seen_spouse_pairs: set[frozenset[int]] = set()

        for child_id, parent_ids in self.parents_of.items():
            for parent_id in parent_ids:
                edges.append(
                    {
                        "id": f"pc-{parent_id}-{child_id}",
                        "source": str(parent_id),
                        "target": str(child_id),
                        "type": models.RelationType.parent_child,
                    }
                )
        for a_id, spouse_ids in self.spouses_of.items():
            for b_id in spouse_ids:
                pair = frozenset({a_id, b_id})
                if pair in seen_spouse_pairs:
                    continue
                seen_spouse_pairs.add(pair)
                edges.append(
                    {
                        "id": f"sp-{a_id}-{b_id}",
                        "source": str(a_id),
                        "target": str(b_id),
                        "type": models.RelationType.spouse,
                    }
                )
        return nodes, edges
