/**
 * Overlay de predição exibido sobre o vídeo da webcam.
 * Mostra label, barra de confiança e latência.
 */
export default function PredictionOverlay({ prediction }) {
  if (!prediction) return null;

  const { label, confidence, latency_ms, dog_detected, smoothed_label } = prediction;

  // Determina a classe CSS baseada no label
  const getLabelClass = (lbl) => {
    switch (lbl) {
      case 'EM_PE':
        return 'standing';
      case 'SENTADO':
        return 'sitting';
      case 'DEITADO':
        return 'lying';
      default:
        return 'no-dog';
    }
  };

  // Traduz o label para exibição
  const getDisplayLabel = (lbl) => {
    switch (lbl) {
      case 'EM_PE':
        return '🐕 Em Pé';
      case 'SENTADO':
        return '🐕 Sentado';
      case 'DEITADO':
        return '🐕 Deitado';
      default:
        return lbl;
    }
  };

  // Cor da barra de confiança
  const getBarColor = (lbl) => {
    switch (lbl) {
      case 'EM_PE':
        return 'var(--color-standing)';
      case 'SENTADO':
        return 'var(--color-sitting)';
      case 'DEITADO':
        return 'var(--color-lying)';
      default:
        return 'var(--color-no-dog)';
    }
  };

  const displayLabel = smoothed_label || label;
  const labelClass = getLabelClass(displayLabel);
  const barColor = getBarColor(displayLabel);

  return (
    <div className="prediction-overlay">
      {!dog_detected && (
        <div style={{ color: 'var(--color-no-dog)', fontSize: '0.8rem', marginBottom: '4px' }}>
          ⚠ Nenhum cão detectado — classificando frame inteiro
        </div>
      )}

      <div className={`prediction-label ${labelClass}`}>
        {getDisplayLabel(displayLabel)}
      </div>

      <div className="confidence-bar-container">
        <div className="confidence-bar">
          <div
            className="confidence-bar-fill"
            style={{
              width: `${confidence * 100}%`,
              backgroundColor: barColor,
            }}
          />
        </div>
        <span className="confidence-text">{(confidence * 100).toFixed(1)}%</span>
      </div>

      <div className="prediction-meta">
        <span>⏱ {latency_ms.toFixed(0)} ms</span>
        <span>🎯 {dog_detected ? 'Cão detectado' : 'Sem detecção'}</span>
      </div>
    </div>
  );
}
