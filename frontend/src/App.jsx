import { useState, useCallback, useEffect, useRef } from 'react';
import WebcamCapture from './components/WebcamCapture';
import PredictionOverlay from './components/PredictionOverlay';
import Dashboard from './components/Dashboard';
import { checkHealth } from './services/api';

/**
 * Componente principal da aplicação.
 * Gerencia estado de predições e integra webcam + dashboard.
 */
export default function App() {
  const [predictions, setPredictions] = useState([]);
  const [currentPrediction, setCurrentPrediction] = useState(null);
  const [isRunning, setIsRunning] = useState(false);
  const [backendOnline, setBackendOnline] = useState(false);
  const healthCheckRef = useRef(null);

  // Callback quando uma nova predição chega
  const handlePrediction = useCallback((result) => {
    setCurrentPrediction(result);
    setPredictions((prev) => {
      const updated = [...prev, result];
      // Mantém apenas os últimos 100 resultados
      return updated.length > 100 ? updated.slice(-100) : updated;
    });
  }, []);

  // Verifica se o backend está online periodicamente
  useEffect(() => {
    const check = async () => {
      const online = await checkHealth();
      setBackendOnline(online);
    };

    check(); // Checa imediatamente
    healthCheckRef.current = setInterval(check, 5000);

    return () => {
      if (healthCheckRef.current) {
        clearInterval(healthCheckRef.current);
      }
    };
  }, []);

  return (
    <div className="app">
      <header className="app-header">
        <h1>🐕 Dog Posture Recognition</h1>
        <p>Reconhecimento de postura canina em tempo real com Inteligência Artificial</p>
      </header>

      <main className="app-content">
        {/* Coluna esquerda: Webcam + Overlay */}
        <div style={{ position: 'relative' }}>
          <WebcamCapture
            onPrediction={handlePrediction}
            isRunning={isRunning}
            setIsRunning={setIsRunning}
          />
          {/* Overlay posicionado sobre o webcam container */}
          {currentPrediction && isRunning && (
            <div style={{
              position: 'absolute',
              bottom: '76px',
              left: '20px',
              right: '20px',
              pointerEvents: 'none',
            }}>
              <PredictionOverlay prediction={currentPrediction} />
            </div>
          )}
        </div>

        {/* Coluna direita: Dashboard */}
        <Dashboard
          predictions={predictions}
          isRunning={isRunning}
          backendOnline={backendOnline}
        />
      </main>
    </div>
  );
}
