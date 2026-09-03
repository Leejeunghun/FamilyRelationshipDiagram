import dagre from 'dagre'
import type { Edge, Node } from 'reactflow'

import type { GraphEdge, GraphNode } from './types'

const NODE_WIDTH = 180
const NODE_HEIGHT = 90
const SPOUSE_GAP = 40

/**
 * dagre는 parent-child 엣지로 세대별(rank/y) 배치를 계산한다.
 * spouse는 dagre가 모르는 개념이지만, 배우자 쌍 사이에 양방향으로 minlen:0 엣지를
 * 추가하면 dagre의 랭크 계산 자체가 두 사람을 같은 세대(rank)로 묶어준다.
 * 이렇게 하면 자녀가 없는 "결혼으로 들어온" 배우자(예: 새로 추가된 사람)도
 * 상대방의 실제 세대를 그대로 따라가며, 반대로 상대방이 잘못 끌려오는 일이 없다.
 */
export function layoutFamilyGraph(
  graphNodes: GraphNode[],
  graphEdges: GraphEdge[],
): { nodes: Node[]; edges: Edge[] } {
  const g = new dagre.graphlib.Graph()
  g.setDefaultEdgeLabel(() => ({}))
  g.setGraph({ rankdir: 'TB', nodesep: 60, ranksep: 100 })

  for (const node of graphNodes) {
    g.setNode(node.id, { width: NODE_WIDTH, height: NODE_HEIGHT })
  }

  const parentChildEdges = graphEdges.filter((e) => e.type === 'parent_child')
  const spouseEdges = graphEdges.filter((e) => e.type === 'spouse')

  for (const edge of parentChildEdges) {
    g.setEdge(edge.source, edge.target)
  }
  for (const edge of spouseEdges) {
    g.setEdge(edge.source, edge.target, { minlen: 0 })
    g.setEdge(edge.target, edge.source, { minlen: 0 })
  }

  dagre.layout(g)

  const positions = new Map<string, { x: number; y: number }>()
  for (const node of graphNodes) {
    const { x, y } = g.node(node.id)
    positions.set(node.id, { x, y })
  }

  // 배우자 쌍은 같은 랭크(y)로 계산되므로, x축으로만 서로 붙여서 나란히 보이게 한다.
  const visitedSpouse = new Set<string>()
  for (const edge of spouseEdges) {
    const pairKey = [edge.source, edge.target].sort().join('|')
    if (visitedSpouse.has(pairKey)) continue
    visitedSpouse.add(pairKey)

    const a = positions.get(edge.source)
    const b = positions.get(edge.target)
    if (!a || !b) continue

    const y = a.y
    const centerX = (a.x + b.x) / 2
    const half = (NODE_WIDTH + SPOUSE_GAP) / 2
    const [leftId, rightId] = a.x <= b.x ? [edge.source, edge.target] : [edge.target, edge.source]
    positions.set(leftId, { x: centerX - half, y })
    positions.set(rightId, { x: centerX + half, y })
  }

  const nodes: Node[] = graphNodes.map((node) => {
    const pos = positions.get(node.id) ?? { x: 0, y: 0 }
    return {
      id: node.id,
      type: 'person',
      position: { x: pos.x - NODE_WIDTH / 2, y: pos.y - NODE_HEIGHT / 2 },
      data: node.data,
    }
  })

  const edges: Edge[] = graphEdges.map((edge) => ({
    id: edge.id,
    source: edge.source,
    target: edge.target,
    type: edge.type === 'spouse' ? 'straight' : 'smoothstep',
    animated: false,
    style:
      edge.type === 'spouse'
        ? { stroke: '#e879f9', strokeDasharray: '4 4' }
        : { stroke: '#94a3b8' },
    label: edge.type === 'spouse' ? '배우자' : undefined,
  }))

  return { nodes, edges }
}
