// Every call to the backend goes through this file. Components never use fetch directly.
import type {
  Assessment,
  AssessmentCreate,
  ModelInfo,
  Patient,
  PatientCreate,
} from './types'

// vite.config.ts proxies /api/* to http://localhost:8000/*
const BASE = '/api'

export class ApiError extends Error {
  readonly status: number

  constructor(status: number, message: string) {
    super(message)
    this.name = 'ApiError'
    this.status = status
  }
}

type PydanticError = { loc?: (string | number)[]; msg?: string }

// FastAPI sends 422 "detail" in two shapes: a string from our services
// ("InvalidInputs: glucose=900 is outside 40-400"), or a list from Pydantic.
function errorMessage(detail: unknown, fallback: string): string {
  if (typeof detail === 'string') return detail
  if (Array.isArray(detail)) {
    return (detail as PydanticError[])
      .map((d) => `${(d.loc ?? []).slice(1).join('.')}: ${d.msg ?? 'invalid'}`)
      .join('; ')
  }
  return fallback
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${BASE}${path}`, {
    ...init,
    headers: { 'Content-Type': 'application/json', ...init?.headers },
  })
  const body: unknown = await response.json().catch(() => null)
  if (!response.ok) {
    const detail = (body as { detail?: unknown } | null)?.detail
    throw new ApiError(response.status, errorMessage(detail, response.statusText))
  }
  return body as T
}

const post = (body: unknown): RequestInit => ({ method: 'POST', body: JSON.stringify(body) })

export const getModels = () => request<ModelInfo[]>('/models')

export const listPatients = () => request<Patient[]>('/patients')
export const getPatient = (id: number) => request<Patient>(`/patients/${id}`)
export const createPatient = (body: PatientCreate) => request<Patient>('/patients', post(body))

export const createAssessment = (body: AssessmentCreate) => request<Assessment>('/assessments', post(body))
export const getAssessment = (id: number) => request<Assessment>(`/assessments/${id}`)
export const getTimeline = (patientId: number) => request<Assessment[]>(`/patients/${patientId}/assessments`)

// Form inputs give strings. A blank must become null, never 0: Number('') === 0,
// which would bring back Pima's fake-zero problem.
export function toInputValue(raw: string): number | null {
  return raw.trim() === '' ? null : Number(raw)
}