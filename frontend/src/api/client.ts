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

// App.tsx sets this, so an expired or revoked token sends the user back to sign-in.
let onUnauthorized = () => {}
export function setUnauthorizedHandler(handler: () => void) {
  onUnauthorized = handler
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

async function request<T>(path: string, token?: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${BASE}${path}`, {
    ...init,
    headers: {
      'Content-Type': 'application/json',
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...init?.headers,
    },
  })
  const body: unknown = await response.json().catch(() => null)
  if (!response.ok) {
    if (response.status === 401 && token) onUnauthorized()
    const detail = (body as { detail?: unknown } | null)?.detail
    throw new ApiError(response.status, errorMessage(detail, response.statusText))
  }
  return body as T
}

const post = (body: unknown): RequestInit => ({ method: 'POST', body: JSON.stringify(body) })

// Public: the model list holds no patient data.
export const getModels = () => request<ModelInfo[]>('/models')

// Everything below needs the token from POST /auth/login (LoginPage does the login itself).
export const listPatients = (token: string) => request<Patient[]>('/patients', token)
export const getPatient = (token: string, id: number) => request<Patient>(`/patients/${id}`, token)
export const createPatient = (token: string, body: PatientCreate) =>
  request<Patient>('/patients', token, post(body))

export const createAssessment = (token: string, body: AssessmentCreate) =>
  request<Assessment>('/assessments', token, post(body))
export const getAssessment = (token: string, id: number) => request<Assessment>(`/assessments/${id}`, token)
export const getTimeline = (token: string, patientId: number) =>
  request<Assessment[]>(`/patients/${patientId}/assessments`, token)

// Form inputs give strings. A blank must become null, never 0: Number('') === 0,
// which would bring back Pima's fake-zero problem.
export function toInputValue(raw: string): number | null {
  return raw.trim() === '' ? null : Number(raw)
}