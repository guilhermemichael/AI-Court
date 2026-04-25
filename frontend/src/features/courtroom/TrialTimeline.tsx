import { Flame, Gavel, Shield, UserRound } from 'lucide-react';
import { motion } from 'framer-motion';

import { MetricCard } from '../../components/MetricCard';
import type { TrialEvent } from '../../lib/api';

type TrialTimelineProps = {
  caseId: string | null;
  status: string;
  events: TrialEvent[];
  allowPrecedents: boolean;
};

export function TrialTimeline({ caseId, status, events, allowPrecedents }: TrialTimelineProps) {
  return (
    <motion.section className="panel panel--timeline" initial={{ opacity: 0, y: 24 }} animate={{ opacity: 1, y: 0 }}>
      <div className="panel-heading">
        <span className="eyebrow">Julgamento em tempo real</span>
        <h2>
          <Gavel size={20} />
          Camara central do tribunal
        </h2>
      </div>

      <div className="status-ribbon">{status}</div>

      <div className="metric-grid">
        <MetricCard label="Caso" value={caseId ? caseId.slice(0, 8).toUpperCase() : 'Aguardando'} />
        <MetricCard label="Etapas emitidas" value={String(events.length)} />
        <MetricCard label="Jurisprudencia" value={allowPrecedents ? 'Ativa' : 'Desligada'} tone={allowPrecedents ? 'green' : 'red'} />
      </div>

      <div className="timeline">
        {events.length === 0 ? (
          <div className="empty-state">
            <UserRound size={20} />
            <p>O escrivao ainda nao abriu a audiencia.</p>
          </div>
        ) : (
          events.map((event) => (
            <motion.article
              className={`timeline-item timeline-item--${roleTone(event.agent_role)}`}
              key={event.sequence_index}
              initial={{ opacity: 0, y: 12 }}
              animate={{ opacity: 1, y: 0 }}
            >
              <div className="timeline-meta">
                <span>#{event.sequence_index}</span>
                <strong>{event.agent_role ?? event.event_type}</strong>
              </div>
              <p>{event.content}</p>
            </motion.article>
          ))
        )}
      </div>

      <div className="courtroom-feed">
        <div>
          <Flame size={18} />
          <span>Promotor em combustao controlada</span>
        </div>
        <div>
          <Shield size={18} />
          <span>Defesa em blindagem emocional</span>
        </div>
        <div>
          <Gavel size={18} />
          <span>Juiz consolidando o entendimento final</span>
        </div>
      </div>
    </motion.section>
  );
}

function roleTone(role: string | null): string {
  if (role === 'PROSECUTOR') {
    return 'prosecutor';
  }
  if (role === 'DEFENDER') {
    return 'defender';
  }
  if (role === 'JUDGE') {
    return 'judge';
  }
  return 'neutral';
}
