const STORAGE_KEY = 'family-tree-owner-id'

/**
 * 로그인 없이 브라우저별로 가족관계도를 구분하기 위한 익명 ID.
 * localStorage에 없으면 새로 만들어 저장하고, 있으면 그대로 재사용한다.
 * 이 ID를 다른 사람과 공유하면 같은 가족관계도를 함께 볼 수 있다(방 코드와 같은 개념).
 */
export function getOwnerId(): string {
  let id = localStorage.getItem(STORAGE_KEY)
  if (!id) {
    id = crypto.randomUUID()
    localStorage.setItem(STORAGE_KEY, id)
  }
  return id
}

export function setOwnerId(id: string) {
  localStorage.setItem(STORAGE_KEY, id)
}
