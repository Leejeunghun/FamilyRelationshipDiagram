import { useEffect, useState } from 'react'
import { Trash2, UserRound, X } from 'lucide-react'

import { api } from '@/lib/api'
import type { Person, RelativesResponse } from '@/lib/types'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import {
  Dialog,
  DialogContent,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'

interface Props {
  person: Person
  onClose: () => void
  onDeleted: () => void
  isEgo: boolean
  onSetEgo: () => void
  onClearEgo: () => void
}

const SECTIONS: { key: keyof RelativesResponse; label: string }[] = [
  { key: 'parents', label: '부모' },
  { key: 'spouses', label: '배우자' },
  { key: 'children', label: '자녀' },
  { key: 'siblings', label: '형제자매' },
  { key: 'cousins', label: '사촌' },
  { key: 'ancestors', label: '조상' },
  { key: 'descendants', label: '자손' },
]

export function PersonDetailsPanel({ person, onClose, onDeleted, isEgo, onSetEgo, onClearEgo }: Props) {
  const [relatives, setRelatives] = useState<RelativesResponse | null>(null)
  const [loading, setLoading] = useState(true)
  const [confirmOpen, setConfirmOpen] = useState(false)

  useEffect(() => {
    let cancelled = false
    setLoading(true)
    api
      .getRelatives(person.id)
      .then((data) => {
        if (!cancelled) setRelatives(data)
      })
      .finally(() => {
        if (!cancelled) setLoading(false)
      })
    return () => {
      cancelled = true
    }
  }, [person.id])

  async function handleDelete() {
    setConfirmOpen(false)
    await api.deletePerson(person.id)
    onDeleted()
  }

  return (
    <Card className="w-72 shrink-0">
      <CardHeader className="flex-row items-center justify-between space-y-0">
        <CardTitle>{person.name}</CardTitle>
        <Button variant="ghost" size="icon" onClick={onClose}>
          <X className="h-4 w-4" />
        </Button>
      </CardHeader>
      <CardContent className="flex flex-col gap-3 text-left">
        <Button
          variant={isEgo ? 'default' : 'outline'}
          size="sm"
          onClick={isEgo ? onClearEgo : onSetEgo}
        >
          <UserRound className="h-4 w-4" />
          {isEgo ? '나 지정 해제' : '이 사람을 나로 보기'}
        </Button>
        {loading && <p className="text-sm text-muted-foreground">불러오는 중...</p>}
        {relatives &&
          SECTIONS.map(({ key, label }) => {
            const list = relatives[key]
            if (list.length === 0) return null
            return (
              <div key={key}>
                <p className="text-xs font-medium text-muted-foreground">{label}</p>
                <p className="text-sm">{list.map((p) => p.name).join(', ')}</p>
              </div>
            )
          })}
        <Button variant="destructive" size="sm" className="mt-2" onClick={() => setConfirmOpen(true)}>
          <Trash2 className="h-4 w-4" />
          사람 삭제
        </Button>
      </CardContent>

      <Dialog open={confirmOpen} onOpenChange={setConfirmOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>{person.name}님을 삭제할까요?</DialogTitle>
          </DialogHeader>
          <p className="text-sm text-muted-foreground">관련된 관계도 함께 삭제됩니다. 이 작업은 되돌릴 수 없습니다.</p>
          <DialogFooter>
            <Button variant="outline" onClick={() => setConfirmOpen(false)}>
              취소
            </Button>
            <Button variant="destructive" onClick={handleDelete}>
              삭제
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </Card>
  )
}
