import { useState, type FormEvent } from 'react'
import { Link2 } from 'lucide-react'

import { api } from '@/lib/api'
import type { Person, RelationType } from '@/lib/types'
import { Button } from '@/components/ui/button'
import {
  Dialog,
  DialogContent,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog'
import { Label } from '@/components/ui/label'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'

interface Props {
  people: Person[]
  onCreated: () => void
}

export function AddRelationshipDialog({ people, onCreated }: Props) {
  const [open, setOpen] = useState(false)
  const [type, setType] = useState<RelationType>('parent_child')
  const [personA, setPersonA] = useState<string>('')
  const [personB, setPersonB] = useState<string>('')
  const [error, setError] = useState<string | null>(null)
  const [submitting, setSubmitting] = useState(false)

  function resetForm() {
    setType('parent_child')
    setPersonA('')
    setPersonB('')
    setError(null)
  }

  async function handleSubmit(e: FormEvent) {
    e.preventDefault()
    if (!personA || !personB) {
      setError('두 사람을 모두 선택하세요')
      return
    }
    if (personA === personB) {
      setError('같은 사람끼리는 관계를 맺을 수 없습니다')
      return
    }
    setSubmitting(true)
    setError(null)
    try {
      await api.createRelationship({
        type,
        person_a_id: Number(personA),
        person_b_id: Number(personB),
      })
      resetForm()
      setOpen(false)
      onCreated()
    } catch (err) {
      setError(err instanceof Error ? err.message : '관계 추가에 실패했습니다')
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <Dialog
      open={open}
      onOpenChange={(next) => {
        setOpen(next)
        if (!next) resetForm()
      }}
    >
      <DialogTrigger asChild>
        <Button size="sm" variant="outline">
          <Link2 className="h-4 w-4" />
          관계 추가
        </Button>
      </DialogTrigger>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>관계 추가</DialogTitle>
        </DialogHeader>
        <form className="flex flex-col gap-3" onSubmit={handleSubmit}>
          <div className="flex flex-col gap-1.5">
            <Label>관계 종류</Label>
            <Select value={type} onValueChange={(v) => setType(v as RelationType)}>
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="parent_child">부모-자녀</SelectItem>
                <SelectItem value="spouse">배우자</SelectItem>
              </SelectContent>
            </Select>
          </div>
          <div className="flex flex-col gap-1.5">
            <Label>{type === 'parent_child' ? '부모' : '사람 A'}</Label>
            <Select value={personA} onValueChange={setPersonA}>
              <SelectTrigger>
                <SelectValue placeholder="선택" />
              </SelectTrigger>
              <SelectContent>
                {people.map((p) => (
                  <SelectItem key={p.id} value={String(p.id)}>
                    {p.name}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
          <div className="flex flex-col gap-1.5">
            <Label>{type === 'parent_child' ? '자녀' : '사람 B'}</Label>
            <Select value={personB} onValueChange={setPersonB}>
              <SelectTrigger>
                <SelectValue placeholder="선택" />
              </SelectTrigger>
              <SelectContent>
                {people.map((p) => (
                  <SelectItem key={p.id} value={String(p.id)}>
                    {p.name}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
          {error && <p className="text-sm text-destructive">{error}</p>}
          <DialogFooter>
            <Button type="submit" disabled={submitting}>
              추가
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  )
}
