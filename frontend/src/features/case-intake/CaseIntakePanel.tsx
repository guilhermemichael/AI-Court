import { Scale, ScrollText } from 'lucide-react';
import { motion } from 'framer-motion';

import type { CasePayload, HouseLaw } from '../../lib/api';

type CaseIntakePanelProps = {
  form: CasePayload;
  laws: HouseLaw[];
  busy: boolean;
  error: string | null;
  onSubmit: () => void;
  onChange: <K extends keyof CasePayload>(key: K, value: CasePayload[K]) => void;
};

export function CaseIntakePanel({ form, laws, busy, error, onSubmit, onChange }: CaseIntakePanelProps) {
  return (
    <motion.aside className="panel panel--intake" initial={{ opacity: 0, x: -24 }} animate={{ opacity: 1, x: 0 }}>
      <div className="panel-heading">
        <span className="eyebrow">Protocole sua treta</span>
        <h2>
          <ScrollText size={20} />
          Ata inicial do processo
        </h2>
      </div>

      <div className="form-grid">
        <Field label="Titulo do caso" value={form.title} onChange={(value) => onChange('title', value)} />
        <Field label="Nome do autor" value={form.plaintiff_name} onChange={(value) => onChange('plaintiff_name', value)} />
        <Field label="Nome do reu" value={form.defendant_name} onChange={(value) => onChange('defendant_name', value)} />
        <Field label="Tipo de conflito" value={form.conflict_type} onChange={(value) => onChange('conflict_type', value)} />
        <div className="field">
          <label>Nivel de drama</label>
          <input
            type="range"
            min="1"
            max="10"
            value={form.drama_level}
            onChange={(event) => onChange('drama_level', Number(event.target.value))}
          />
          <div className="range-readout">{form.drama_level}/10</div>
        </div>
        <TextField label="Narrativa do autor" value={form.plaintiff_argument} onChange={(value) => onChange('plaintiff_argument', value)} />
        <TextField label="Narrativa do reu" value={form.defendant_argument} onChange={(value) => onChange('defendant_argument', value)} />

        <label className="toggle-row">
          <input
            type="checkbox"
            checked={form.allow_precedents}
            onChange={(event) => onChange('allow_precedents', event.target.checked)}
          />
          <span>Permitir jurisprudencia e memoria institucional</span>
        </label>

        <button className="action-button" disabled={busy} onClick={onSubmit}>
          <Scale size={18} />
          {busy ? 'Julgando em tempo real...' : 'Protocolar e iniciar julgamento'}
        </button>

        {error ? <p className="error-banner">{error}</p> : null}
      </div>

      <div className="law-preview">
        <h3>Leis da Casa</h3>
        <ul className="law-list">
          {laws.map((law) => (
            <li key={law.id}>
              <strong>{law.article_number}</strong>
              <span>{law.description}</span>
            </li>
          ))}
        </ul>
      </div>
    </motion.aside>
  );
}

function Field({ label, value, onChange }: { label: string; value: string; onChange: (value: string) => void }) {
  return (
    <div className="field">
      <label>{label}</label>
      <input value={value} onChange={(event) => onChange(event.target.value)} />
    </div>
  );
}

function TextField({ label, value, onChange }: { label: string; value: string; onChange: (value: string) => void }) {
  return (
    <div className="field">
      <label>{label}</label>
      <textarea value={value} onChange={(event) => onChange(event.target.value)} />
    </div>
  );
}
