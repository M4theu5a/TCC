function Sparkline({ data, color }) {
  if (!data || data.length < 2) {
    return (
      <svg width="100%" height="28" viewBox="0 0 100 28" preserveAspectRatio="none">
        <polyline points="0,14 100,14" stroke={color} strokeWidth="1.5" fill="none" opacity="0.4" />
      </svg>
    );
  }
  const max = Math.max(...data);
  const min = Math.min(...data);
  const range = max - min || 1;
  const points = data
    .map((v, i) => {
      const x = (i / (data.length - 1)) * 100;
      const y = 24 - ((v - min) / range) * 20;
      return `${x},${y}`;
    })
    .join(' ');
  return (
    <svg width="100%" height="28" viewBox="0 0 100 28" preserveAspectRatio="none">
      <polyline points={points} stroke={color} strokeWidth="1.5" fill="none" />
    </svg>
  );
}

function MetricsPanel({ fps, avgLatency, avgConfidence, totalPredictions, fpsHistory, latencyHistory, confidenceHistory, predCountHistory }) {
  const metrics = [
    {
      label: 'FPS Atual',
      number: fps > 0 ? fps.toFixed(1) : '0.0',
      unit: 'frames/seg',
      color: '#3b82f6',
      history: fpsHistory,
    },
    {
      label: 'Latência Média',
      number: avgLatency > 0 ? avgLatency : '0',
      unit: 'ms por frame',
      color: '#16a34a',
      history: latencyHistory,
    },
    {
      label: 'Confiança Média',
      number: avgConfidence > 0 ? avgConfidence.toFixed(1) : '0.0',
      unit: 'últimos 30s',
      color: '#d97706',
      history: confidenceHistory,
    },
    {
      label: 'Predições',
      number: totalPredictions.toLocaleString('pt-BR'),
      unit: 'total hoje',
      color: '#8b5cf6',
      history: predCountHistory,
    },
  ];

  return (
    <div className="card">
      <h2 className="card-title">Métricas em Tempo Real</h2>
      <div className="metrics-grid">
        {metrics.map((m) => (
          <div key={m.label} className="metric-card">
            <p className="metric-card-label">{m.label}</p>
            <div className="metric-card-value">
              <span className="metric-number">{m.number}</span>
              <span className="metric-unit">{m.unit}</span>
            </div>
            <Sparkline data={m.history} color={m.color} />
          </div>
        ))}
      </div>
    </div>
  );
}

export default MetricsPanel;
