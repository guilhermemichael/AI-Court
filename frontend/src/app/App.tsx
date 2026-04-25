import { useDeferredValue, useEffect, useRef, useState, startTransition } from 'react';
import { motion } from 'framer-motion';
import { Landmark, Sparkles } from 'lucide-react';

import { CaseIntakePanel } from '../features/case-intake/CaseIntakePanel';
import { TrialTimeline } from '../features/courtroom/TrialTimeline';
import { VerdictPanel } from '../features/verdict/VerdictPanel';
import { createCase, getCase, listLaws, type CasePayload, type HouseLaw, type TrialEvent, type VerdictSummary } from '../lib/api';
import { openTrialSocket } from '../lib/socket';
import { casePayloadSchema, defaultCaseForm } from '../lib/validators';
import { startTrial } from '../lib/api';

export function App() {
  const [form, setForm] = useState<CasePayload>(defaultCaseForm);
  const [laws, setLaws] = useState<HouseLaw[]>([]);
  const [caseId, setCaseId] = useState<string | null>(null);
  const [events, setEvents] = useState<TrialEvent[]>([]);
  const [verdict, setVerdict] = useState<VerdictSummary | null>(null);
  const [status, setStatus] = useState('Pronto para protocolar uma nova treta.');
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const socketRef = useRef<WebSocket | null>(null);
  const deferredEvents = useDeferredValue(events);

  useEffect(() => {
    void listLaws()
      .then(setLaws)
      .catch(() => {
        setLaws([]);
      });

    return () => {
      socketRef.current?.close();
    };
  }, []);

  async function runProtocol() {
    setBusy(true);
    setError(null);
    setVerdict(null);
    setEvents([]);
    setStatus('Protocolando o caso e abrindo a sessao do tribunal.');

    try {
      const payload = casePayloadSchema.parse(form);
      const created = await createCase(payload);
      setCaseId(created.id);

      socketRef.current?.close();
      socketRef.current = openTrialSocket(created.id, {
        onReady: (message) => setStatus(message),
        onStatus: (_nextStatus, content) => setStatus(content),
        onEvent: (event) => {
          startTransition(() => {
            setEvents((current) => upsertEvent(current, event));
          });
        },
        onVerdict: (liveVerdict) => {
          setStatus(`Sentenca publicada: ${liveVerdict.sentence}`);
        },
      });

      await waitForSocketReady(socketRef.current);
      const trial = await startTrial(created.id);
      const fullCase = await getCase(created.id);
      setEvents(fullCase.events);
      setVerdict(fullCase.verdict ?? trial.verdict);
      setStatus('Julgamento encerrado. Documento oficial disponivel para consulta.');
    } catch (caughtError) {
      setError('Nao foi possivel concluir o julgamento. Verifique a stack local e tente novamente.');
      setStatus('Sessao interrompida por falha operacional.');
      console.error(caughtError);
    } finally {
      setBusy(false);
    }
  }

  function handleChange<K extends keyof CasePayload>(key: K, value: CasePayload[K]) {
    setForm((current) => ({ ...current, [key]: value }));
  }

  return (
    <main className="app-shell">
      <motion.header className="hero" initial={{ opacity: 0, y: -18 }} animate={{ opacity: 1, y: 0 }}>
        <div className="hero-copy">
          <span className="eyebrow eyebrow--light">AI Court</span>
          <h1>O Supremo Tribunal das IAs Domesticas</h1>
          <p>Onde conflitos banais recebem sentencas absurdamente oficiais.</p>
        </div>

        <div className="hero-badges">
          <div className="hero-badge">
            <Landmark size={20} />
            <span>Deliberacao multiagente</span>
          </div>
          <div className="hero-badge">
            <Sparkles size={20} />
            <span>Julgamento em tempo real</span>
          </div>
        </div>
      </motion.header>

      <section className="court-layout">
        <CaseIntakePanel form={form} laws={laws} busy={busy} error={error} onSubmit={runProtocol} onChange={handleChange} />
        <TrialTimeline caseId={caseId} status={status} events={deferredEvents} allowPrecedents={form.allow_precedents} />
        <VerdictPanel caseId={caseId} verdict={verdict} />
      </section>
    </main>
  );
}

function upsertEvent(current: TrialEvent[], incoming: TrialEvent): TrialEvent[] {
  const existing = current.findIndex((item) => item.sequence_index === incoming.sequence_index);
  if (existing >= 0) {
    const cloned = [...current];
    cloned[existing] = incoming;
    return cloned;
  }
  return [...current, incoming].sort((left, right) => left.sequence_index - right.sequence_index);
}

function waitForSocketReady(socket: WebSocket | null): Promise<void> {
  if (!socket || socket.readyState === WebSocket.OPEN) {
    return Promise.resolve();
  }

  return new Promise((resolve, reject) => {
    const handleOpen = () => {
      socket.removeEventListener('open', handleOpen);
      socket.removeEventListener('error', handleError);
      resolve();
    };
    const handleError = () => {
      socket.removeEventListener('open', handleOpen);
      socket.removeEventListener('error', handleError);
      reject(new Error('socket_connection_failed'));
    };

    socket.addEventListener('open', handleOpen, { once: true });
    socket.addEventListener('error', handleError, { once: true });
  });
}
