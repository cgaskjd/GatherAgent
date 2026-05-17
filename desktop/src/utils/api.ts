const API_BASE = 'http://localhost:18790';

export interface ChatRequest {
  message: string;
  session_id?: string;
  model?: string;
  provider?: string;
  base_url?: string;
  api_key?: string;
  mode?: string;
}

export interface ChatResponse {
  content: string;
  tool_calls?: ToolCall[];
  usage?: { input_tokens: number; output_tokens: number };
  session_id: string;
}

export interface ToolCall {
  name: string;
  arguments: string;
  result?: string;
}

export interface ModelPreset {
  label: string;
  model_id: string;
  provider: string;
}

export interface SessionInfo {
  id: string;
  title: string;
  created_at: string;
  message_count: number;
}

export interface AppConfig {
  model: { default: string; provider: string; base_url: string | null; api_key: string | null };
  agent: { mode: string; max_iterations: number };
}

export async function sendChat(req: ChatRequest): Promise<ChatResponse> {
  const res = await fetch(`${API_BASE}/api/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(req),
  });
  if (!res.ok) throw new Error(`Chat error: ${res.statusText}`);
  return res.json();
}

export async function getModels(): Promise<ModelPreset[]> {
  const res = await fetch(`${API_BASE}/api/models`);
  if (!res.ok) return [];
  return res.json();
}

export async function switchModel(model: string, provider: string, base_url?: string, api_key?: string): Promise<void> {
  await fetch(`${API_BASE}/api/models/switch`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ model, provider, base_url, api_key }),
  });
}

export async function getConfig(): Promise<AppConfig> {
  const res = await fetch(`${API_BASE}/api/config`);
  if (!res.ok) throw new Error('Failed to fetch config');
  return res.json();
}

export async function updateConfig(config: Partial<AppConfig>): Promise<void> {
  await fetch(`${API_BASE}/api/config`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(config),
  });
}

export async function getSessions(): Promise<SessionInfo[]> {
  const res = await fetch(`${API_BASE}/api/sessions`);
  if (!res.ok) return [];
  return res.json();
}

export async function createSession(): Promise<SessionInfo> {
  const res = await fetch(`${API_BASE}/api/sessions`, { method: 'POST' });
  if (!res.ok) throw new Error('Failed to create session');
  return res.json();
}

export async function deleteSession(id: string): Promise<void> {
  await fetch(`${API_BASE}/api/sessions/${id}`, { method: 'DELETE' });
}

export async function healthCheck(): Promise<boolean> {
  try {
    const res = await fetch(`${API_BASE}/api/health`, { signal: AbortSignal.timeout(3000) });
    return res.ok;
  } catch {
    return false;
  }
}
