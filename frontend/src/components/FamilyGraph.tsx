import { useCallback, useEffect, useMemo, useState } from 'react'
import ReactFlow, {
  Background,
  Controls,
  MiniMap,
  useEdgesState,
  useNodesState,
  type Node,
  type NodeMouseHandler,
} from 'reactflow'
import 'reactflow/dist/style.css'

import { api } from '@/lib/api'
import { layoutFamilyGraph } from '@/lib/layout'
import type { Person } from '@/lib/types'
import { PersonNode } from '@/components/PersonNode'

const nodeTypes = { person: PersonNode }

interface Props {
  refreshTrigger: number
  onSelectPerson: (person: Person) => void
  egoPersonId?: number | null
  kinshipTerms?: Record<number, string>
}

export function FamilyGraph({ refreshTrigger, onSelectPerson, egoPersonId, kinshipTerms }: Props) {
  const [nodes, setNodes, onNodesChange] = useNodesState([])
  const [edges, setEdges, onEdgesChange] = useEdgesState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    let cancelled = false
    setLoading(true)
    setError(null)
    api
      .getGraph()
      .then(({ nodes: graphNodes, edges: graphEdges }) => {
        if (cancelled) return
        const { nodes: laidOutNodes, edges: laidOutEdges } = layoutFamilyGraph(graphNodes, graphEdges)
        setNodes(laidOutNodes)
        setEdges(laidOutEdges)
      })
      .catch((err) => {
        if (!cancelled) setError(err instanceof Error ? err.message : '그래프를 불러오지 못했습니다')
      })
      .finally(() => {
        if (!cancelled) setLoading(false)
      })
    return () => {
      cancelled = true
    }
  }, [refreshTrigger, setNodes, setEdges])

  const handleNodeClick = useCallback<NodeMouseHandler>(
    (_, node: Node<Person>) => {
      onSelectPerson(node.data)
    },
    [onSelectPerson],
  )

  const isEmpty = useMemo(() => !loading && !error && nodes.length === 0, [loading, error, nodes.length])

  // 레이아웃(nodes)은 그래프가 바뀔 때만 다시 계산하고, 호칭/나 표시는
  // 여기서 화면에 보여줄 데이터에만 얹어서 매번 레이아웃을 새로 계산하지 않는다.
  const displayNodes = useMemo(
    () =>
      nodes.map((node) => ({
        ...node,
        data: {
          ...node.data,
          isEgo: egoPersonId != null && node.data.id === egoPersonId,
          kinshipTerm: kinshipTerms?.[node.data.id],
        },
      })),
    [nodes, egoPersonId, kinshipTerms],
  )

  return (
    <div className="relative h-full w-full">
      {error && (
        <div className="absolute inset-x-0 top-0 z-10 bg-destructive px-4 py-2 text-sm text-destructive-foreground">
          {error} (백엔드 서버가 실행 중인지 확인하세요)
        </div>
      )}
      {isEmpty && (
        <div className="absolute inset-0 z-10 flex items-center justify-center text-sm text-muted-foreground">
          아직 등록된 사람이 없습니다. "사람 추가" 버튼으로 시작해보세요.
        </div>
      )}
      <ReactFlow
        nodes={displayNodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onNodeClick={handleNodeClick}
        nodeTypes={nodeTypes}
        fitView
        minZoom={0.2}
      >
        <Background />
        <Controls />
        <MiniMap pannable zoomable className="!bg-card" />
      </ReactFlow>
    </div>
  )
}
