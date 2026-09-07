export type Gender = 'male' | 'female' | 'unknown'
export type RelationType = 'parent_child' | 'spouse'

export interface Person {
  id: number
  name: string
  gender: Gender
  birth_date: string | null
  death_date: string | null
  photo_url: string | null
}

export type PersonInput = Omit<Person, 'id'>

export interface Relationship {
  id: number
  type: RelationType
  person_a_id: number
  person_b_id: number
}

export type RelationshipInput = Omit<Relationship, 'id'>

export interface GraphNode {
  id: string
  data: Person
}

export interface GraphEdge {
  id: string
  source: string
  target: string
  type: RelationType
}

export interface GraphResponse {
  nodes: GraphNode[]
  edges: GraphEdge[]
}

export interface RelativesResponse {
  parents: Person[]
  children: Person[]
  spouses: Person[]
  siblings: Person[]
  ancestors: Person[]
  descendants: Person[]
  cousins: Person[]
}

export interface KinshipTerm {
  person: Person
  term: string
}
