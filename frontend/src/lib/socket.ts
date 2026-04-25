export type TrialSocketHandlers = {
  onReady?: (message: string) => void;
  onStatus?: (status: string, content: string) => void;
  onEvent?: (event: {
    sequence_index: number;
    event_type: string;
    agent_role: string | null;
    content: string;
    metadata: Record<string, unknown>;
    created_at: string | null;
  }) => void;
  onVerdict?: (payload: { sentence: string; guilt_index: number; winner: string }) => void;
};

const WS_BASE_URL = import.meta.env.VITE_WS_BASE_URL ?? 'ws://localhost:8000';

export function openTrialSocket(caseId: string, handlers: TrialSocketHandlers): WebSocket {
  const socket = new WebSocket(`${WS_BASE_URL}/api/v1/ws/trials/${caseId}`);

  socket.onmessage = (event) => {
    const payload = JSON.parse(event.data) as {
      type: string;
      content?: string;
      status?: string;
      sequence_index?: number;
      agent_role?: string | null;
      metadata?: Record<string, unknown>;
      created_at?: string | null;
      sentence?: string;
      guilt_index?: number;
      winner?: string;
    };

    if (payload.type === 'SOCKET_READY' && payload.content) {
      handlers.onReady?.(payload.content);
      return;
    }

    if (payload.type === 'TRIAL_STATUS' && payload.status && payload.content) {
      handlers.onStatus?.(payload.status, payload.content);
      return;
    }

    if (payload.type === 'VERDICT_READY' && payload.sentence && payload.guilt_index !== undefined && payload.winner) {
      handlers.onVerdict?.({
        sentence: payload.sentence,
        guilt_index: payload.guilt_index,
        winner: payload.winner,
      });
      return;
    }

    if (payload.sequence_index !== undefined && payload.content) {
      handlers.onEvent?.({
        sequence_index: payload.sequence_index,
        event_type: payload.type,
        agent_role: payload.agent_role ?? null,
        content: payload.content,
        metadata: payload.metadata ?? {},
        created_at: payload.created_at ?? null,
      });
    }
  };

  return socket;
}
