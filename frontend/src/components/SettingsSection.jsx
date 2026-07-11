function SettingsSection({ captureFps, onChangeCaptureFps }) {
  return (
    <div className="card" style={{ maxWidth: 480 }}>
      <h2 className="card-title">Configurações</h2>

      <div className="settings-row">
        <div className="settings-row-label">
          <span>Taxa de captura</span>
          <span>{captureFps} FPS</span>
        </div>
        <p className="settings-row-desc">
          Quantos frames por segundo são enviados da webcam para a API de
          predição. Valores mais altos aumentam a responsividade, mas
          também a carga no backend.
        </p>
        <input
          type="range"
          min="1"
          max="10"
          step="1"
          value={captureFps}
          onChange={(e) => onChangeCaptureFps(Number(e.target.value))}
          className="settings-slider"
        />
      </div>
    </div>
  );
}

export default SettingsSection;
