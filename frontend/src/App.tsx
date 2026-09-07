import { useCallback, useEffect, useState } from 'react'

import { api } from '@/lib/api'
import type { Person } from '@/lib/types'
import { AddPersonDialog } from '@/components/AddPersonDialog'
import { AddRelationshipDialog } from '@/components/AddRelationshipDialog'
import { FamilyGraph } from '@/components/FamilyGraph'
import { OwnerIdDialog } from '@/components/OwnerIdDialog'
import { PersonDetailsPanel } from '@/components/PersonDetailsPanel'

function App() {
  const [people, setPeople] = useState<Person[]>([])
  const [refreshTrigger, setRefreshTrigger] = useState(0)
  const [selectedPerson, setSelectedPerson] = useState<Person | null>(null)
  const [egoPersonId, setEgoPersonId] = useState<number | null>(null)
  const [kinshipTerms, setKinshipTerms] = useState<Record<number, string>>({})

  const refresh = useCallback(() => setRefreshTrigger((v) => v + 1), [])

  useEffect(() => {
    api.getPeople().then(setPeople).catch(() => setPeople([]))
  }, [refreshTrigger])

  // "나"로 지정된 사람이 바뀌거나 데이터가 갱신될 때마다 호칭을 다시 계산한다.
  useEffect(() => {
    if (egoPersonId == null) {
      setKinshipTerms({})
      return
    }
    let cancelled = false
    api
      .getKinshipTerms(egoPersonId)
      .then((terms) => {
        if (cancelled) return
        setKinshipTerms(Object.fromEntries(terms.map((t) => [t.person.id, t.term])))
      })
      .catch(() => {
        if (!cancelled) setKinshipTerms({})
      })
    return () => {
      cancelled = true
    }
  }, [egoPersonId, refreshTrigger])

  return (
    <div className="flex h-screen flex-col">
      <header className="flex items-center justify-between border-b px-4 py-3">
        <h1 className="text-lg font-semibold">가족관계도</h1>
        <div className="flex gap-2">
          <OwnerIdDialog />
          <AddRelationshipDialog people={people} onCreated={refresh} />
          <AddPersonDialog onCreated={refresh} />
        </div>
      </header>
      <main className="flex min-h-0 flex-1 gap-3 p-3">
        <div className="min-w-0 flex-1 rounded-lg border">
          <FamilyGraph
            refreshTrigger={refreshTrigger}
            onSelectPerson={setSelectedPerson}
            egoPersonId={egoPersonId}
            kinshipTerms={kinshipTerms}
          />
        </div>
        {selectedPerson && (
          <PersonDetailsPanel
            person={selectedPerson}
            onClose={() => setSelectedPerson(null)}
            onDeleted={() => {
              setSelectedPerson(null)
              if (egoPersonId === selectedPerson.id) setEgoPersonId(null)
              refresh()
            }}
            isEgo={egoPersonId === selectedPerson.id}
            onSetEgo={() => setEgoPersonId(selectedPerson.id)}
            onClearEgo={() => setEgoPersonId(null)}
          />
        )}
      </main>
    </div>
  )
}

export default App
