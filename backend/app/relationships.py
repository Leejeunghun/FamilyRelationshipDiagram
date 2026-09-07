"""parent-child / spouse 두 종류의 저장된 관계만으로 형제/조상/자손/사촌 등을 계산한다."""

from collections import defaultdict

from sqlalchemy.orm import Session

from app import crud, models


class FamilyGraph:
    """전체 Person/Relationship을 한 번 읽어 메모리 상의 인접 리스트로 구성."""

    def __init__(self, db: Session, owner_id: str):
        self.people: dict[int, models.Person] = {p.id: p for p in crud.get_people(db, owner_id)}
        self.parents_of: dict[int, set[int]] = defaultdict(set)
        self.children_of: dict[int, set[int]] = defaultdict(set)
        self.spouses_of: dict[int, set[int]] = defaultdict(set)

        for rel in crud.get_relationships(db, owner_id):
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

    def _ancestor_paths(self, person_id: int, max_depth: int) -> dict[int, list[int]]:
        """person_id에서 조상까지의 최단 경로. path[0]=직계 부모, path[-1]=그 조상 자신."""
        paths: dict[int, list[int]] = {}

        def dfs(current_id: int, path: list[int]):
            for parent_id in self.parents_of.get(current_id, ()):
                new_path = path + [parent_id]
                if parent_id not in paths or len(new_path) < len(paths[parent_id]):
                    paths[parent_id] = new_path
                if len(new_path) < max_depth:
                    dfs(parent_id, new_path)

        dfs(person_id, [])
        return paths

    def _is_older(self, a_id: int, b_id: int) -> bool | None:
        """a가 b보다 나이가 많은지. 생년월일이 하나라도 없으면 알 수 없음(None)."""
        a, b = self.people.get(a_id), self.people.get(b_id)
        if a is None or b is None or a.birth_date is None or b.birth_date is None:
            return None
        return a.birth_date < b.birth_date

    def _side_prefix(self, parent: models.Person) -> str:
        """부모의 성별로 친가/외가 구분 접두사를 반환. 성별 미상이면 빈 문자열."""
        if parent.gender == models.Gender.male:
            return "친"
        if parent.gender == models.Gender.female:
            return "외"
        return ""

    def _ancestor_term(self, up: int, target_id: int, path: list[int]) -> str | None:
        target = self.people[target_id]
        if up == 1:
            return {"male": "아버지", "female": "어머니"}.get(target.gender.value, "부모")
        if up == 2:
            prefix = self._side_prefix(self.people[path[0]])
            if target.gender == models.Gender.male:
                return f"{prefix}할아버지"
            if target.gender == models.Gender.female:
                return f"{prefix}할머니"
            return f"{prefix}조부모" if prefix else "조부모"
        return None

    def _descendant_term(self, down: int, target_id: int) -> str | None:
        target = self.people[target_id]
        if down == 1:
            return {"male": "아들", "female": "딸"}.get(target.gender.value, "자녀")
        if down == 2:
            return {"male": "손자", "female": "손녀"}.get(target.gender.value, "손주")
        return None

    def _sibling_term(self, ego_id: int, target_id: int) -> str:
        """형/오빠/누나/언니는 '말하는 사람(ego)'의 성별에 따라 달라진다."""
        ego, target = self.people[ego_id], self.people[target_id]
        older = self._is_older(target_id, ego_id)
        if older is False:
            return "동생"
        if older is True:
            if target.gender == models.Gender.male:
                return "형" if ego.gender == models.Gender.male else "오빠"
            if target.gender == models.Gender.female:
                return "누나" if ego.gender == models.Gender.male else "언니"
        return "형제자매"

    def _uncle_aunt_term(self, up_path: list[int], target_id: int) -> str:
        """up_path[0] = ego의 직계 부모(공유 조부모까지의 첫 걸음) = 친가/외가를 가른다."""
        parent = self.people[up_path[0]]
        target = self.people[target_id]
        if parent.gender == models.Gender.male:  # 아버지 쪽
            if target.gender == models.Gender.male:
                older = self._is_older(target_id, up_path[0])
                if older is True:
                    return "큰아버지"
                if older is False:
                    return "작은아버지"
                return "삼촌"
            if target.gender == models.Gender.female:
                return "고모"
        elif parent.gender == models.Gender.female:  # 어머니 쪽
            if target.gender == models.Gender.male:
                return "외삼촌"
            if target.gender == models.Gender.female:
                return "이모"
        return "삼촌" if target.gender == models.Gender.male else "고모"

    def _cousin_term(self, up_path: list[int], down_path: list[int]) -> str:
        """up_path[0]=ego 쪽 부모(친/외), down_path[0]=그 형제자매(고모/이모/삼촌 등)."""
        ego_parent = self.people[up_path[0]]
        connecting = self.people[down_path[0]]
        if ego_parent.gender == models.Gender.male:
            return "고종사촌" if connecting.gender == models.Gender.female else "사촌"
        if ego_parent.gender == models.Gender.female:
            return "이종사촌" if connecting.gender == models.Gender.female else "외사촌"
        return "사촌"

    def kinship_term(self, ego_id: int, target_id: int) -> str | None:
        """ego 입장에서 target을 부르는 호칭. 혈족만 지원, 4촌까지만 계산.
        (범위 밖이거나 혈연관계가 없으면 None)"""
        if ego_id == target_id:
            return None
        if target_id in self.spouses_of.get(ego_id, ()):
            return "배우자"

        max_depth = 2
        ego_ancestors = self._ancestor_paths(ego_id, max_depth)
        target_ancestors = self._ancestor_paths(target_id, max_depth)

        if ego_id in target_ancestors:  # target이 ego의 자손
            return self._descendant_term(len(target_ancestors[ego_id]), target_id)
        if target_id in ego_ancestors:  # target이 ego의 조상
            return self._ancestor_term(len(ego_ancestors[target_id]), target_id, ego_ancestors[target_id])

        common = set(ego_ancestors) & set(target_ancestors)
        if not common:
            return None
        best = min(common, key=lambda a: len(ego_ancestors[a]) + len(target_ancestors[a]))
        up_path, down_path = ego_ancestors[best], target_ancestors[best]
        up, down = len(up_path), len(down_path)

        if up == 1 and down == 1:
            return self._sibling_term(ego_id, target_id)
        if up == 2 and down == 1:
            return self._uncle_aunt_term(up_path, target_id)
        if up == 1 and down == 2:
            return "조카"
        if up == 2 and down == 2:
            return self._cousin_term(up_path, down_path)
        return None  # 5촌 이상 등 계산 범위 밖

    def kinship_terms_for(self, ego_id: int) -> list[tuple[models.Person, str]]:
        """ego를 기준으로, 계산 가능한 모든 사람의 호칭 목록."""
        results = []
        for pid, person in self.people.items():
            term = self.kinship_term(ego_id, pid)
            if term:
                results.append((person, term))
        return results

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
