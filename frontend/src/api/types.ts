// Mirrors backend/app/schemas/*.py. If a schema changes there, change it here too.

export interface InputSpec {
  min: number
  max: number
  optional: boolean
}

export interface ModelInfo {
  model_version: string
  features: string[]
  inputs: Record<string, InputSpec>
  metrics: Record<string, number>
}

export interface Patient {
  id: number
  identifier: string
  date_of_birth: string // YYYY-MM-DD
  created_at: string
}

export interface PatientCreate {
  identifier: string
  date_of_birth: string // YYYY-MM-DD
}

export type RiskLevel = 'low' | 'moderate' | 'high'

// One bar of the explanation chart. Positive contribution pushes toward diabetes.
export interface Contribution {
  feature: string
  value: number | null
  contribution: number
}

export interface Assessment {
  id: number
  patient_id: number
  model_version: string
  inputs: Record<string, number | null>
  risk_probability: number
  risk_level: RiskLevel
  shap_values: Contribution[] // sorted, largest effect first
  created_at: string
}

export interface AssessmentCreate {
  patient_id: number
  model_version: string
  // every feature of the model; null = left blank (optional features only)
  inputs: Record<string, number | null>
}