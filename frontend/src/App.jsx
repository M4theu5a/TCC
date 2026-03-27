/**
 * App.jsx - Componente Principal
 * 
 * Orquestra todos os componentes:
 * - Verificação de saúde do backend
 * - Captura da webcam
 * - Envio de frames para predição
 * - Exibição de métricas
 */

import { useState, useEffect, useCallback, useRef } from 'react';
import WebcamCapture from './components/WebcamCapture';
import MetricsPanel from './components/MetricsPanel';
import { checkHealth, predictFrame } from './services/api';

function App() {
  // Estados principais
  const [isRunning, setIsRunning] = useState(false);
  const [serverStatus, setServerStatus] = useState('connecting'); // 'online' | 'offline' | 'connecting'
  const [prediction, setPrediction] = useState(null);

  // Métricas
  const [latency, setLatency] = useState(0);
  const [fps, setFps] = useState(0);
  const [confidence, setConfidence] = useState(0);

  // Controle de FPS
  const frameCountRef = useRef(0);
  const fpsIntervalRef = useRef(null);

  // Verifica saúde do backend ao iniciar
  useEffect(() => {
    const checkServer = async () => {
      const health = await checkHealth();
      setServerStatus(health.status === 'online' ? 'online' : 'offline');
    };

    checkServer();

    // Verifica a cada 10 segundos
    const interval = setInterval(checkServer, 10000);
    return () => clearInterval(interval);
  }, []);

  // Contador de FPS
  useEffect(() => {
    if (isRunning) {
      frameCountRef.current = 0;
      fpsIntervalRef.current = setInterval(() => {
        setFps(frameCountRef.current);
        frameCountRef.current = 0;
      }, 1000);
    } else {
      if (fpsIntervalRef.current) {
        clearInterval(fpsIntervalRef.current);
      }
      setFps(0);
    }

    return () => {
      if (fpsIntervalRef.current) {
        clearInterval(fpsIntervalRef.current);
      }
    };
  }, [isRunning]);

  // Callback chamado a cada frame capturado
  const handleFrame = useCallback(async (blob) => {
    const startTime = performance.now();

    const result = await predictFrame(blob);

    const totalLatency = Math.round(performance.now() - startTime);

    setPrediction(result);
    setLatency(result.latency_ms || totalLatency);
    setConfidence(result.confidence || 0);
    frameCountRef.current += 1;
  }, []);

  // Handlers dos botões
  const handleStart = () => {
    if (serverStatus !== 'online') {
      alert('O servidor backend não está online. Inicie o backend primeiro.');
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

  // Texto do status
  const statusText = {
    online: 'Servidor Online',
    offline: 'Servidor Offline',
    connecting: 'Conectando...',
  };

  return (
    <div className="app">
      {/* Header */}
      <header className="app-header">
        <h1>🐶 Reconhecimento de Postura de Cães</h1>
        <p>TCC - Engenharia de Computação</p>
      </header>

      {/* Status do servidor */}
      <div style={{ textAlign: 'center' }}>
        <span className={`status-badge ${serverStatus}`}>
          <span className="status-dot"></span>
          {statusText[serverStatus]}
        </span>
      </div>

      {/* Webcam */}
      <WebcamCapture
        isRunning={isRunning}
        onFrame={handleFrame}
        fps={5}
        prediction={prediction}
      />

      {/* Métricas */}
      <MetricsPanel
        latency={latency}
        fps={fps}
        confidence={confidence}
      />

      {/* Controles */}
      <div className="controls">
        {!isRunning ? (
          <button
            className="btn btn-start"
            onClick={handleStart}
            disabled={serverStatus !== 'online'}
          >
            ▶ Iniciar
          </button>
        ) : (
          <button className="btn btn-stop" onClick={handleStop}>
            ■ Parar
          </button>
        )}
      </div>
    </div>
  );
}

export default App;
