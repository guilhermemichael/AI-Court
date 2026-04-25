type MetricCardProps = {
  label: string;
  value: string;
  tone?: 'gold' | 'green' | 'red';
};

export function MetricCard({ label, value, tone = 'gold' }: MetricCardProps) {
  return (
    <article className={`metric-card metric-card--${tone}`}>
      <span>{label}</span>
      <strong>{value}</strong>
    </article>
  );
}
