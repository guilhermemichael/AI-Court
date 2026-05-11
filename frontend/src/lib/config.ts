const LOCAL_API_BASE_URL = 'http://localhost:8000';
const LOCAL_WS_BASE_URL = 'ws://localhost:8000';

export const API_BASE_URL = normalizeBaseUrl(import.meta.env.VITE_API_BASE_URL, LOCAL_API_BASE_URL);
export const WS_BASE_URL = normalizeBaseUrl(
  import.meta.env.VITE_WS_BASE_URL,
  deriveWebSocketBaseUrl(API_BASE_URL),
);

function normalizeBaseUrl(value: string | undefined, fallback: string): string {
  return (value?.trim() || fallback).replace(/\/+$/, '');
}

function deriveWebSocketBaseUrl(apiBaseUrl: string): string {
  try {
    const url = new URL(apiBaseUrl);
    url.protocol = url.protocol === 'https:' ? 'wss:' : 'ws:';
    return normalizeBaseUrl(url.toString(), LOCAL_WS_BASE_URL);
  } catch {
    return LOCAL_WS_BASE_URL;
  }
}
