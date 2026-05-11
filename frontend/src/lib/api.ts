import { API_BASE_URL } from './config';

export type CasePayload = {
  title: string;
  plaintiff_name: string;
  defendant_name: string;
  plaintiff_argument: string;
  defendant_argument: string;
  conflict_type: string;
  drama_level: number;
  allow_precedents: boolean;
};

export type TrialEvent = {
  sequence_index: number;
  event_type: string;
  agent_role: string | null;
  content: string;
  metadata: Record<string, unknown>;
  created_at: string | null;
};

export type VerdictSummary = {
  winner: string;
  guilt_index: number;
  sentence: string;
  reasoning: string;
  compensation_order: string | null;
  appeal_allowed: boolean;
};

export type CaseDetail = {
  id: string;
  title: string;
  plaintiff_name: string;
  defendant_name: string;
  conflict_type: string;
  drama_level: number;
  allow_precedents: boolean;
  status: string;
  events: TrialEvent[];
  verdict: VerdictSummary | null;
};

export type HouseLaw = {
  id: number;
  title: string;
  article_number: string;
  description: string;
  severity: number;
};

async function parseJson<T>(response: Response): Promise<T> {
  if (!response.ok) {
    throw new Error(`api_request_failed:${response.status}`);
  }
  return response.json() as Promise<T>;
}

export async function createCase(payload: CasePayload): Promise<{ id: string; status: string; title: string }> {
  const response = await fetch(`${API_BASE_URL}/api/v1/cases`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  return parseJson(response);
}

export async function startTrial(caseId: string): Promise<{ verdict: VerdictSummary; status: string }> {
  const response = await fetch(`${API_BASE_URL}/api/v1/trials/${caseId}/start`, { method: 'POST' });
  return parseJson(response);
}

export async function getCase(caseId: string): Promise<CaseDetail> {
  const response = await fetch(`${API_BASE_URL}/api/v1/cases/${caseId}`);
  return parseJson(response);
}

export async function listLaws(): Promise<HouseLaw[]> {
  const response = await fetch(`${API_BASE_URL}/api/v1/laws`);
  const payload = await parseJson<{ items: HouseLaw[] }>(response);
  return payload.items;
}

export function verdictPdfUrl(caseId: string): string {
  return `${API_BASE_URL}/api/v1/pdfs/${caseId}`;
}
