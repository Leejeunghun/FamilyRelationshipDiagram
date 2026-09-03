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

  const refresh = useCallback(() => setRefreshTrigger((v) => v + 1), [])

  useEffect(() => {
    api.getPeople().then(setPeople).catch(() => setPeople([]))
  }, [refreshTrigger])

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
          <FamilyGraph refreshTrigger={refreshTrigger} onSelectPerson={setSelectedPerson} />
        </div>
        {selectedPerson && (
          <PersonDetailsPanel
            person={selectedPerson}
            onClose={() => setSelectedPerson(null)}
            onDeleted={() => {
              setSelectedPerson(null)
              refresh()
            }}
          />
        )}
      </main>
    </div>
  )
}

export default App
