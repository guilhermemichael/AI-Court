import { Download, Scale, ScrollText } from 'lucide-react';
import { motion } from 'framer-motion';

import { MetricCard } from '../../components/MetricCard';
import type { VerdictSummary } from '../../lib/api';
import { verdictPdfUrl } from '../../lib/api';

type VerdictPanelProps = {
  caseId: string | null;
  verdict: VerdictSummary | null;
};

export function VerdictPanel({ caseId, verdict }: VerdictPanelProps) {
  return (
    <motion.aside className="panel panel--verdict" initial={{ opacity: 0, x: 24 }} animate={{ opacity: 1, x: 0 }}>
      <div className="panel-heading">
        <span className="eyebrow">Dispositivo final</span>
        <h2>
          <Scale size={20} />
          Sentenca e reparacao
        </h2>
      </div>

      {!verdict ? (
        <div className="empty-state empty-state--verdict">
          <ScrollText size={20} />
          <p>A sentenca oficial aparecera aqui assim que o Juiz IA encerrar a deliberacao.</p>
        </div>
      ) : (
        <>
          <div className="metric-grid metric-grid--compact">
            <MetricCard label="Vencedor" value={verdict.winner} tone="green" />
            <MetricCard label="Indice de culpa" value={verdict.guilt_index.toFixed(2)} tone="gold" />
          </div>

          <article className="verdict-card">
            <span className="stamp">Sentenca transitada em julgado</span>
            <p className="verdict-sentence">{verdict.sentence}</p>
            <p className="verdict-reasoning">{verdict.reasoning}</p>
            <p className="verdict-compensation">
              <strong>Pena aplicada:</strong> {verdict.compensation_order ?? 'Sem ordem compensatoria adicional.'}
            </p>
          </article>

          <div className="verdict-actions">
            {caseId ? (
              <a className="action-button action-button--secondary" href={verdictPdfUrl(caseId)} target="_blank" rel="noreferrer">
                <Download size={18} />
                Baixar PDF oficial
              </a>
            ) : null}
            <button className="ghost-button" disabled>
              Entrar com recurso
            </button>
          </div>
        </>
      )}
    </motion.aside>
  );
}
