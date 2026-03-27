import { useState, useRef, useEffect, useCallback } from 'react';
import { predictFrame } from '../services/api';

const CAPTURE_INTERVAL_MS = 200; // ~5 FPS

/**
 * Componente de captura de webcam.
 * Captura frames e envia para o backend a cada 200ms.
 */
export default function WebcamCapture({ onPrediction, isRunning, setIsRunning }) {
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const streamRef = useRef(null);
  const intervalRef = useRef(null);
  const [error, setError] = useState(null);
  const [cameraReady, setCameraReady] = useState(false);

  // Inicia a câmera
  const startCamera = useCallback(async () => {
    setError(null);
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: {
          width: { ideal: 640 },
          height: { ideal: 480 },
          facingMode: 'environment',
        },
        audio: false,
      });

      streamRef.current = stream;

      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        videoRef.current.onloadedmetadata = () => {
          videoRef.current.play();
          setCameraReady(true);
        };
      }
    } catch (err) {
      console.error('Erro ao acessar câmera:', err);
      setError(
        err.name === 'NotAllowedError'
          ? 'Acesso à câmera negado. Permita o acesso nas configurações do navegador.'
          : 'Erro ao acessar câmera. Verifique se há uma câmera conectada.'
      );
    }
  }, []);

  // Para a câmera
  const stopCamera = useCallback(() => {
    if (intervalRef.current) {
      clearInterval(intervalRef.current);
      intervalRef.current = null;
    }

    if (streamRef.current) {
      streamRef.current.getTracks().forEach((track) => track.stop());
      streamRef.current = null;
    }

    setCameraReady(false);
    setIsRunning(false);
  }, [setIsRunning]);

  // Captura um frame e envia para predição
  const captureFrame = useCallback(async () => {
    if (!videoRef.current || !canvasRef.current || !cameraReady) return;

    const video = videoRef.current;
    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');

    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    ctx.drawImage(video, 0, 0);

    const base64 = canvas.toDataURL('image/jpeg', 0.7);

    try {
      const result = await predictFrame(base64);
      onPrediction(result);
    } catch (err) {
      console.warn('Erro na predição:', err.message);
    }
  }, [cameraReady, onPrediction]);

  // Toggle inferência
  const toggleInference = useCallback(() => {
    if (isRunning) {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
        intervalRef.current = null;
      }
      setIsRunning(false);
    } else {
      intervalRef.current = setInterval(captureFrame, CAPTURE_INTERVAL_MS);
      setIsRunning(true);
    }
  }, [isRunning, captureFrame, setIsRunning]);

  // Cleanup ao desmontar
  useEffect(() => {
    return () => {
      stopCamera();
    };
  }, [stopCamera]);

  return (
    <div className="glass-card">
      <div className="card-header">
        <span className="icon">📹</span>
        <h2>Câmera</h2>
        <span
          className={`status-dot ${cameraReady ? 'active' : 'inactive'}`}
          style={{ marginLeft: 'auto' }}
        />
      </div>
      <div className="card-body">
        <div className="webcam-container" id="webcam-container">
          {error ? (
            <div className="webcam-placeholder">
              <span className="icon">⚠️</span>
              <p>{error}</p>
            </div>
          ) : !cameraReady ? (
            <div className="webcam-placeholder">
              <span className="icon">📷</span>
              <p>Clique em "Iniciar Câmera" para começar</p>
            </div>
          ) : null}
          <video
            ref={videoRef}
            autoPlay
            playsInline
            muted
            style={{ display: cameraReady ? 'block' : 'none' }}
          />
          <canvas ref={canvasRef} />
          {/* Overlay é renderizado pelo componente pai */}
        </div>

        <div className="camera-controls">
          {!cameraReady ? (
            <button className="btn btn-primary" onClick={startCamera} id="btn-start-camera">
              📷 Iniciar Câmera
            </button>
          ) : (
            <>
              <button
                className={`btn ${isRunning ? 'btn-danger' : 'btn-primary'}`}
                onClick={toggleInference}
                id="btn-toggle-inference"
              >
                {isRunning ? '⏸ Pausar' : '▶ Iniciar Análise'}
              </button>
              <button className="btn btn-danger" onClick={stopCamera} id="btn-stop-camera">
                ⏹ Parar Câmera
              </button>
            </>
          )}
        </div>
      </div>
    </div>
  );
}
