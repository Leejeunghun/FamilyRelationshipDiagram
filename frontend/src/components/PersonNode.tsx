import { memo } from 'react'
import { Handle, Position, type NodeProps } from 'reactflow'
import { User } from 'lucide-react'

import type { Person } from '@/lib/types'
import { cn } from '@/lib/utils'

function formatYears(person: Person) {
  const birth = person.birth_date ? person.birth_date.slice(0, 4) : '?'
  const death = person.death_date ? person.death_date.slice(0, 4) : ''
  if (!person.birth_date && !person.death_date) return null
  return death ? `${birth} - ${death}` : `${birth} -`
}

function PersonNodeImpl({ data, selected }: NodeProps<Person>) {
  const years = formatYears(data)
  return (
    <div
      className={cn(
        'flex w-[180px] items-center gap-3 rounded-lg border bg-card px-3 py-2.5 shadow-sm transition-shadow',
        selected ? 'border-primary ring-2 ring-ring' : 'border-border',
        data.gender === 'male' && 'border-l-4 border-l-sky-400',
        data.gender === 'female' && 'border-l-4 border-l-rose-400',
      )}
    >
      <Handle type="target" position={Position.Top} className="!bg-muted-foreground" />
      <div className="flex h-9 w-9 shrink-0 items-center justify-center overflow-hidden rounded-full bg-muted">
        {data.photo_url ? (
          <img src={data.photo_url} alt={data.name} className="h-full w-full object-cover" />
        ) : (
          <User className="h-4 w-4 text-muted-foreground" />
        )}
      </div>
      <div className="min-w-0 text-left">
        <p className="truncate text-sm font-medium">{data.name}</p>
        {years && <p className="truncate text-xs text-muted-foreground">{years}</p>}
      </div>
      <Handle type="source" position={Position.Bottom} className="!bg-muted-foreground" />
    </div>
  )
}

export const PersonNode = memo(PersonNodeImpl)
