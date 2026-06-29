import { useState, useEffect, useCallback, useRef } from "react";
import WebcamCapture from "./components/WebcamCapture";
import MetricsPanel from "./components/MetricsPanel";
import { checkHealth, predictFrame } from "./services/api";

const LABEL_CONFIG = {
  EM_PE:   { label: "EM PÉ",   color: "#16a34a", bg: "#dcfce7" },
  SENTADO: { label: "SENTADO", color: "#d97706", bg: "#fef3c7" },
  DEITADO: { label: "DEITADO", color: "#2563eb", bg: "#dbeafe" },
};

const POSTURAS = [
  { key: "EM_PE",   label: "EM PÉ",   desc: "Cão erguido sobre as quatro patas",                color: "#16a34a", bg: "#dcfce7" },
  { key: "SENTADO", label: "SENTADO", desc: "Cão com os quartos traseiros apoiados no chão",     color: "#d97706", bg: "#fef3c7" },
  { key: "DEITADO", label: "DEITADO", desc: "Cão com o corpo inteiro sobre o chão",              color: "#2563eb", bg: "#dbeafe" },
];

const PIPELINE = [
  { icon: "📷", name: "1. Captura",      desc: "Frame da webcam" },
  { icon: "→",  arrow: true },
  { icon: "⊕",  name: "2. Envio",        desc: "~5 FPS para API" },
  { icon: "→",  arrow: true },
  { icon: "🧠", name: "3. IA (Backend)", desc: "Detecção + Classificação" },
  { icon: "→",  arrow: true },
  { icon: "📊", name: "4. Resposta",     desc: "JSON com resultados" },
  { icon: "→",  arrow: true },
  { icon: "🖥️", name: "5. Exibição",    desc: "Overlay em tempo real" },
];

function App() {
  const [isRunning, setIsRunning]     = useState(false);
  const [serverStatus, setServerStatus] = useState("connecting");
  const [prediction, setPrediction]   = useState(null);
  const [latency, setLatency]         = useState(0);
  const [fps, setFps]                 = useState(0);
  const [confidence, setConfidence]   = useState(0);
  const [history, setHistory]         = useState([]);
  const [totalPredictions, setTotalPredictions] = useState(0);
  const [avgLatency, setAvgLatency]   = useState(0);
  const [avgConfidence, setAvgConfidence] = useState(0);

  const [fpsHistory, setFpsHistory]               = useState([]);
  const [latencyHistory, setLatencyHistory]       = useState([]);
  const [confidenceHistory, setConfidenceHistory] = useState([]);
  const [predCountHistory, setPredCountHistory]   = useState([]);

  const frameCountRef     = useRef(0);
  const fpsIntervalRef    = useRef(null);
  const latencyWindowRef  = useRef([]);
  const confWindowRef     = useRef([]);

  useEffect(() => {
    const check = async () => {
      const health = await checkHealth();
      setServerStatus(health.status === "online" ? "online" : "offline");
    };
    check();
    const id = setInterval(check, 10000);
    return () => clearInterval(id);
  }, []);

  useEffect(() => {
    if (isRunning) {
      frameCountRef.current = 0;
      fpsIntervalRef.current = setInterval(() => {
        const current = frameCountRef.current;
        setFps(current);
        setFpsHistory((prev) => [...prev.slice(-19), current]);
        frameCountRef.current = 0;
      }, 1000);
    } else {
      if (fpsIntervalRef.current) clearInterval(fpsIntervalRef.current);
      setFps(0);
    }
    return () => { if (fpsIntervalRef.current) clearInterval(fpsIntervalRef.current); };
  }, [isRunning]);

  const handleFrame = useCallback(async (blob) => {
    const t0 = performance.now();
    const result = await predictFrame(blob);
    const totalLat = Math.round(performance.now() - t0);

    const lat  = result.latency_ms || totalLat;
    const conf = result.confidence || 0;

    setPrediction(result);
    setLatency(lat);
    setConfidence(conf);
    frameCountRef.current += 1;

    latencyWindowRef.current = [...latencyWindowRef.current.slice(-29), lat];
    confWindowRef.current    = [...confWindowRef.current.slice(-29), conf * 100];

    setLatencyHistory([...latencyWindowRef.current]);
    setConfidenceHistory([...confWindowRef.current]);

    const avg = (arr) => arr.reduce((a, b) => a + b, 0) / arr.length;
    setAvgLatency(Math.round(avg(latencyWindowRef.current)));
    setAvgConfidence(avg(confWindowRef.current));

    if (result.label && result.label !== "ERRO") {
      const entry = {
        id:         Date.now(),
        label:      result.label,
        confidence: conf,
        latency:    lat,
        time:       new Date().toLocaleTimeString("pt-BR", { hour: "2-digit", minute: "2-digit", second: "2-digit" }),
      };
      setHistory((prev) => [entry, ...prev.slice(0, 9)]);
      setTotalPredictions((prev) => {
        const next = prev + 1;
        setPredCountHistory((ph) => [...ph.slice(-19), next]);
        return next;
      });
    }
  }, []);

  const handleStart = () => {
    if (serverStatus !== "online") {
      alert("O servidor backend não está online. Inicie o backend primeiro.");
      return;
    }
    setIsRunning(true);
  };

  const handleStop = () => {
    setIsRunning(false);
    setPrediction(null);
    setLatency(0);
    setConfidence(0);
  };

  const currentCfg = prediction && LABEL_CONFIG[prediction.label];

  const statusText = {
    online:     "API Conectada",
    offline:    "API Offline",
    connecting: "Conectando...",
  };

  return (
    <div className="layout">
      {/* ── Sidebar ── */}
      <aside className="sidebar">
        <div className="sidebar-logo">
          <div className="logo-icon">🐾</div>
          <div className="logo-text">
            <span className="logo-title">Dog Posture</span>
            <span className="logo-subtitle">Recognition</span>
          </div>
        </div>

        <nav className="sidebar-nav">
          {[
            { icon: "⊞", label: "Dashboard",      active: true },
            { icon: "📋", label: "Sobre o Projeto" },
            { icon: "📊", label: "Métricas" },
            { icon: "⚙️", label: "Configurações" },
            { icon: "📄", label: "Documentação" },
          ].map((item) => (
            <a key={item.label} href="#" className={`nav-item${item.active ? " active" : ""}`}>
              <span className="nav-icon">{item.icon}</span>
              {item.label}
            </a>
          ))}
        </nav>

        <div className="sidebar-status">
          <p className="status-title">Status do Sistema</p>
          <p className="status-online-line">
            <span className="dot" style={{ color: "#4ade80" }} />
            Online
          </p>
          <div className="status-row">
            <span>Backend (API)</span>
            <span className={serverStatus === "online" ? "tag-online" : "tag-offline"}>
              <span className="dot" />
              {serverStatus === "online" ? "Online" : "Offline"}
            </span>
          </div>
          <div className="status-row">
            <span>Modelo de IA</span>
            <span className="tag-loaded">
              <span className="dot" />
              Carregado
            </span>
          </div>
        </div>

        <div className="sidebar-footer">
          <span className="footer-paw">🐾</span>
          <div>
            <p className="footer-title">TCC</p>
            <p className="footer-sub">Engenharia de Computação</p>
          </div>
        </div>
      </aside>

      {/* ── Main ── */}
      <main className="main">
        {/* Header */}
        <div className="main-header">
          <div>
            <h1 className="main-title">Reconhecimento de Postura de Cães</h1>
            <p className="main-subtitle">
              Classificação de postura em tempo real usando Visão Computacional e IA
            </p>
          </div>
          <div className="header-actions">
            <span className={`api-badge ${serverStatus}`}>
              <span className="dot" />
              {statusText[serverStatus]}
            </span>
          </div>
        </div>

        {/* Content */}
        <div className="content-grid">
          {/* ── Left column ── */}
          <div className="left-col">
            {/* Câmera ao Vivo */}
            <div className="card">
              <div className="card-header-row">
                <h2 className="card-title">Câmera ao Vivo</h2>
                {isRunning && (
                  <button className="btn-stop" onClick={handleStop}>■ Parar</button>
                )}
              </div>
              <WebcamCapture
                isRunning={isRunning}
                onFrame={handleFrame}
                fps={5}
                prediction={prediction}
                latency={latency}
                currentFps={fps}
                onStart={handleStart}
                serverStatus={serverStatus}
              />
            </div>

            {/* Como funciona */}
            <div className="card">
              <h2 className="card-title">Como funciona</h2>
              <div className="pipeline">
                {PIPELINE.map((item, i) =>
                  item.arrow ? (
                    <span key={i} className="pipeline-arrow">→</span>
                  ) : (
                    <div key={i} className="pipeline-step">
                      <div className="pipeline-icon-wrap">{item.icon}</div>
                      <p className="pipeline-name">{item.name}</p>
                      <p className="pipeline-desc">{item.desc}</p>
                    </div>
                  )
                )}
              </div>
            </div>

            {/* Métricas */}
            <MetricsPanel
              fps={fps}
              avgLatency={avgLatency}
              avgConfidence={avgConfidence}
              totalPredictions={totalPredictions}
              fpsHistory={fpsHistory}
              latencyHistory={latencyHistory}
              confidenceHistory={confidenceHistory}
              predCountHistory={predCountHistory}
            />
          </div>

          {/* ── Right column ── */}
          <div className="right-col">
            {/* Predição Atual */}
            <div className="card">
              <h2 className="card-title">Predição Atual</h2>
              <div className="prediction-current">
                <div
                  className="prediction-dog-icon"
                  style={{ background: currentCfg?.bg || "#f1f5f9" }}
                >
                  🐕
                </div>
                <div>
                  <p
                    className="prediction-label-text"
                    style={{ color: currentCfg?.color || "#94a3b8" }}
                  >
                    {currentCfg?.label || (isRunning ? "Aguardando..." : "—")}
                  </p>
                  <p className="confidence-sub">Confiança</p>
                  <p className="confidence-value" style={{ color: currentCfg?.color || "#94a3b8" }}>
                    {confidence > 0 ? `${(confidence * 100).toFixed(1)}%` : "—"}
                  </p>
                  <div className="confidence-bar-bg">
                    <div
                      className="confidence-bar-fill"
                      style={{
                        width: `${(confidence * 100).toFixed(0)}%`,
                        background: currentCfg?.color || "#e2e8f0",
                      }}
                    />
                  </div>
                </div>
              </div>
              <div className="prediction-stats">
                <div className="pred-stat">
                  <span className="pred-stat-icon">⏱</span>
                  <div>
                    <p className="pred-stat-label">Latência</p>
                    <p className="pred-stat-value">{latency > 0 ? `${latency} ms` : "— ms"}</p>
                  </div>
                </div>
                <div className="pred-stat">
                  <span className="pred-stat-icon">⚡</span>
                  <div>
                    <p className="pred-stat-label">FPS</p>
                    <p className="pred-stat-value">{fps > 0 ? fps.toFixed(1) : "—"}</p>
                  </div>
                </div>
              </div>
            </div>

            {/* Posturas */}
            <div className="card">
              <div className="card-header-row">
                <h2 className="card-title">Posturas</h2>
                <a href="#" className="card-link">Saiba mais ⓘ</a>
              </div>
              {POSTURAS.map((p) => (
                <div
                  key={p.key}
                  className={`posture-item${prediction?.label === p.key ? " active" : ""}`}
                >
                  <div className="posture-icon" style={{ background: p.bg }}>
                    <span style={{ color: p.color }}>🐕</span>
                  </div>
                  <div>
                    <p className="posture-label" style={{ color: p.color }}>{p.label}</p>
                    <p className="posture-desc">{p.desc}</p>
                  </div>
                </div>
              ))}
            </div>

            {/* Histórico */}
            <div className="card">
              <div className="card-header-row">
                <h2 className="card-title">Histórico de Predições</h2>
                <a href="#" className="card-link">Ver todas</a>
              </div>
              {history.length === 0 ? (
                <p className="history-empty">Nenhuma predição ainda.</p>
              ) : (
                <div className="history-list">
                  {history.map((entry) => {
                    const cfg = LABEL_CONFIG[entry.label];
                    return (
                      <div key={entry.id} className="history-item">
                        <span className="history-dot" style={{ background: cfg?.color }} />
                        <span className="history-label" style={{ color: cfg?.color }}>
                          {cfg?.label || entry.label}
                        </span>
                        <span className="history-conf">
                          {(entry.confidence * 100).toFixed(1)}%
                        </span>
                        <span className="history-lat">{entry.latency} ms</span>
                        <span className="history-time">{entry.time}</span>
                      </div>
                    );
                  })}
                </div>
              )}
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}

export default App;
