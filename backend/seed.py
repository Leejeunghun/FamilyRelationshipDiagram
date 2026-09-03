"""샘플 3세대 가족 데이터를 DB에 채워 넣는 스크립트.

사용법: backend 폴더에서 `python seed.py`
"""

from app import models
from app.database import Base, SessionLocal, engine

Base.metadata.create_all(bind=engine)

SEED_OWNER_ID = "seed-demo"

db = SessionLocal()

try:
    if db.query(models.Person).filter(models.Person.owner_id == SEED_OWNER_ID).count() > 0:
        print("이미 시드 데이터가 존재합니다. 초기화하려면 family_tree.db 파일을 삭제하세요.")
    else:
        people = {
            "조부": models.Person(owner_id=SEED_OWNER_ID, name="김할아버지", gender=models.Gender.male),
            "조모": models.Person(owner_id=SEED_OWNER_ID, name="이할머니", gender=models.Gender.female),
            "부": models.Person(owner_id=SEED_OWNER_ID, name="김아버지", gender=models.Gender.male),
            "모": models.Person(owner_id=SEED_OWNER_ID, name="박어머니", gender=models.Gender.female),
            "삼촌": models.Person(owner_id=SEED_OWNER_ID, name="김삼촌", gender=models.Gender.male),
            "숙모": models.Person(owner_id=SEED_OWNER_ID, name="최숙모", gender=models.Gender.female),
            "나": models.Person(owner_id=SEED_OWNER_ID, name="김나", gender=models.Gender.unknown),
            "동생": models.Person(owner_id=SEED_OWNER_ID, name="김동생", gender=models.Gender.unknown),
            "사촌": models.Person(owner_id=SEED_OWNER_ID, name="김사촌", gender=models.Gender.unknown),
        }
        db.add_all(people.values())
        db.commit()
        for p in people.values():
            db.refresh(p)

        def pc(parent_key, child_key):
            db.add(
                models.Relationship(
                    owner_id=SEED_OWNER_ID,
                    type=models.RelationType.parent_child,
                    person_a_id=people[parent_key].id,
                    person_b_id=people[child_key].id,
                )
            )

        def sp(a_key, b_key):
            db.add(
                models.Relationship(
                    owner_id=SEED_OWNER_ID,
                    type=models.RelationType.spouse,
                    person_a_id=people[a_key].id,
                    person_b_id=people[b_key].id,
                )
            )

        sp("조부", "조모")
        pc("조부", "부")
        pc("조모", "부")
        pc("조부", "삼촌")
        pc("조모", "삼촌")

        sp("부", "모")
        pc("부", "나")
        pc("모", "나")
        pc("부", "동생")
        pc("모", "동생")

        sp("삼촌", "숙모")
        pc("삼촌", "사촌")
        pc("숙모", "사촌")

        db.commit()
        print(f"샘플 데이터 {len(people)}명 생성 완료.")
finally:
    db.close()
