/**
 * Componente MetricsPanel
 * 
 * Exibe as métricas de performance em tempo real:
 * - Latência (ms)
 * - FPS efetivo
 * - Confiança média
 */

function MetricsPanel({ latency, fps, confidence }) {
  return (
    <div className="metrics-panel">
      <div className="metric-card">
        <div className="metric-value">{latency} ms</div>
        <div className="metric-label">Latência</div>
      </div>
      <div className="metric-card">
        <div className="metric-value">{fps}</div>
        <div className="metric-label">FPS</div>
      </div>
      <div className="metric-card">
        <div className="metric-value">
          {confidence > 0 ? `${(confidence * 100).toFixed(1)}%` : '—'}
        </div>
        <div className="metric-label">Confiança</div>
      </div>
    </div>
  );
}

export default MetricsPanel;
