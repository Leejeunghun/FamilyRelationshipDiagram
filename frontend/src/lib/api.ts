import type {
  GraphResponse,
  Person,
  PersonInput,
  RelationshipInput,
  RelativesResponse,
} from './types'
import { getOwnerId } from './ownerId'

const API_URL = import.meta.env.VITE_API_URL ?? 'http://localhost:8000'

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${API_URL}${path}`, {
    headers: { 'Content-Type': 'application/json', 'X-Owner-Id': getOwnerId() },
    ...options,
  })
  if (!res.ok) {
    const body = await res.json().catch(() => null)
    throw new Error(body?.detail ?? `요청 실패: ${res.status}`)
  }
  if (res.status === 204) return undefined as T
  return res.json() as Promise<T>
}

export const api = {
  getGraph: () => request<GraphResponse>('/graph'),
  getPeople: () => request<Person[]>('/people'),
  createPerson: (data: PersonInput) =>
    request<Person>('/people', { method: 'POST', body: JSON.stringify(data) }),
  deletePerson: (id: number) => request<void>(`/people/${id}`, { method: 'DELETE' }),
  createRelationship: (data: RelationshipInput) =>
    request<void>('/relationships', { method: 'POST', body: JSON.stringify(data) }),
  deleteRelationship: (id: number) => request<void>(`/relationships/${id}`, { method: 'DELETE' }),
  getRelatives: (personId: number) => request<RelativesResponse>(`/people/${personId}/relatives`),
  uploadPhoto: async (file: File): Promise<{ url: string }> => {
    const formData = new FormData()
    formData.append('file', file)
    const res = await fetch(`${API_URL}/upload/photo`, { method: 'POST', body: formData })
    if (!res.ok) {
      const body = await res.json().catch(() => null)
      throw new Error(body?.detail ?? `업로드 실패: ${res.status}`)
    }
    return res.json()
  },
}
