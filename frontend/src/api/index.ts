// The backend has no auth yet, so the token is accepted and ignored for now.
import * as client from './client'
import type { AssessmentCreate, PatientCreate } from './types'

export const listModels = (_token?: string) => client.getModels()
export const listPatients = (_token?: string) => client.listPatients()
export const createPatient = (_token: string | undefined, body: PatientCreate) => client.createPatient(body)
export const createAssessment = (_token: string | undefined, body: AssessmentCreate) => client.createAssessment(body)
export const listAssessments = (_token: string | undefined, patientId: number) => client.getTimeline(patientId)