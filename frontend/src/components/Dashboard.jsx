import { useMemo } from 'react';

/**
 * Dashboard com métricas em tempo real.
 * Exibe FPS, latência média, e histórico de predições.
 */
export default function Dashboard({ predictions, isRunning, backendOnline }) {
  // Calcula métricas a partir do histórico
  const metrics = useMemo(() => {
    if (predictions.length === 0) {
      return {
        avgLatency: 0,
        fps: 0,
        totalFrames: 0,
        dogDetectionRate: 0,
      };
    }

    const latencies = predictions.map((p) => p.latency_ms);
    const avgLatency = latencies.reduce((a, b) => a + b, 0) / latencies.length;

    // Calcula FPS real baseado nos últimos 10 frames
    const recent = predictions.slice(-10);
    const fps = recent.length > 0 ? 1000 / (avgLatency + 200) : 0; // 200ms interval

    const dogDetected = predictions.filter((p) => p.dog_detected).length;
    const dogDetectionRate = (dogDetected / predictions.length) * 100;

    return {
      avgLatency: avgLatency.toFixed(0),
      fps: fps.toFixed(1),
      totalFrames: predictions.length,
      dogDetectionRate: dogDetectionRate.toFixed(0),
    };
  }, [predictions]);

  // Conta distribuição de classes
  const classDistribution = useMemo(() => {
    const counts = { EM_PE: 0, SENTADO: 0, DEITADO: 0 };
    predictions.forEach((p) => {
      const label = p.smoothed_label || p.label;
      if (counts[label] !== undefined) {
        counts[label]++;
      }
    });
    return counts;
  }, [predictions]);

  // Últimas 10 predições (mais recentes primeiro)
  const recentPredictions = useMemo(() => {
    return [...predictions].reverse().slice(0, 10);
  }, [predictions]);

  const getDisplayLabel = (label) => {
    switch (label) {
      case 'EM_PE': return 'Em Pé';
      case 'SENTADO': return 'Sentado';
      case 'DEITADO': return 'Deitado';
      default: return label;
    }
  };

  const getLabelColor = (label) => {
    switch (label) {
      case 'EM_PE': return 'var(--color-standing)';
      case 'SENTADO': return 'var(--color-sitting)';
      case 'DEITADO': return 'var(--color-lying)';
      default: return 'var(--color-no-dog)';
    }
  };

  return (
    <div className="dashboard">
      {/* Status da conexão */}
      <div className={`connection-status ${backendOnline ? 'connected' : 'disconnected'}`}>
        <span className={`status-dot ${backendOnline ? 'active' : 'inactive'}`} />
        <span>{backendOnline ? 'Backend conectado' : 'Backend offline'}</span>
      </div>

      {/* Métricas */}
      <div className="glass-card">
        <div className="card-header">
          <span className="icon">📊</span>
          <h2>Métricas</h2>
        </div>
        <div className="card-body">
          <div className="metrics-grid">
            <div className="metric-item">
              <div className="metric-value">{metrics.fps}</div>
              <div className="metric-label">FPS</div>
            </div>
            <div className="metric-item">
              <div className="metric-value">{metrics.avgLatency}</div>
              <div className="metric-label">Latência (ms)</div>
            </div>
            <div className="metric-item">
              <div className="metric-value">{metrics.totalFrames}</div>
              <div className="metric-label">Frames</div>
            </div>
            <div className="metric-item">
              <div className="metric-value">{metrics.dogDetectionRate}%</div>
              <div className="metric-label">Detecção</div>
            </div>
          </div>
        </div>
      </div>

      {/* Distribuição de classes */}
      <div className="glass-card">
        <div className="card-header">
          <span className="icon">📈</span>
          <h2>Distribuição</h2>
        </div>
        <div className="card-body">
          {Object.entries(classDistribution).map(([label, count]) => {
            const total = predictions.length || 1;
            const pct = ((count / total) * 100).toFixed(0);
            return (
              <div key={label} style={{ marginBottom: '10px' }}>
                <div style={{
                  display: 'flex',
                  justifyContent: 'space-between',
                  marginBottom: '4px',
                  fontSize: '0.8rem'
                }}>
                  <span style={{ color: getLabelColor(label), fontWeight: 600 }}>
                    {getDisplayLabel(label)}
                  </span>
                  <span style={{ color: 'var(--text-muted)' }}>{pct}% ({count})</span>
                </div>
                <div className="confidence-bar" style={{ height: '4px' }}>
                  <div
                    className="confidence-bar-fill"
                    style={{
                      width: `${pct}%`,
                      backgroundColor: getLabelColor(label),
                    }}
                  />
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Histórico recente */}
      <div className="glass-card">
        <div className="card-header">
          <span className="icon">🕐</span>
          <h2>Histórico</h2>
        </div>
        <div className="card-body">
          {recentPredictions.length === 0 ? (
            <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem', textAlign: 'center' }}>
              {isRunning ? 'Aguardando predições...' : 'Inicie a análise para ver o histórico'}
            </p>
          ) : (
            <ul className="history-list">
              {recentPredictions.map((p, i) => (
                <li key={i} className="history-item">
                  <span className="label" style={{ color: getLabelColor(p.smoothed_label || p.label) }}>
                    {getDisplayLabel(p.smoothed_label || p.label)}
                  </span>
                  <span className="confidence">{(p.confidence * 100).toFixed(0)}%</span>
                  <span className="latency">{p.latency_ms.toFixed(0)}ms</span>
                </li>
              ))}
            </ul>
          )}
        </div>
      </div>
    </div>
  );
}
