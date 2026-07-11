import { useRef, useEffect, useCallback } from 'react';

const LABELS_PT = {
  EM_PE: 'Em Pé',
  SENTADO: 'Sentado',
  DEITADO: 'Deitado',
};

function WebcamCapture({ isRunning, onFrame, fps = 5, prediction, latency, currentFps, onStart, serverStatus }) {
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const streamRef = useRef(null);
  const intervalRef = useRef(null);

  const startWebcam = useCallback(async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: { width: { ideal: 640 }, height: { ideal: 480 }, facingMode: 'user' },
      });
      streamRef.current = stream;
      if (videoRef.current) videoRef.current.srcObject = stream;
    } catch (error) {
      console.error('Erro ao acessar webcam:', error);
      alert('Não foi possível acessar a webcam. Verifique as permissões do navegador.');
    }
  }, []);

  const stopWebcam = useCallback(() => {
    if (streamRef.current) {
      streamRef.current.getTracks().forEach((track) => track.stop());
      streamRef.current = null;
    }
    if (videoRef.current) videoRef.current.srcObject = null;
  }, []);

  const captureFrame = useCallback(() => {
    const video = videoRef.current;
    const canvas = canvasRef.current;
    if (!video || !canvas || video.readyState < 2) return;
    const ctx = canvas.getContext('2d');
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    ctx.drawImage(video, 0, 0);
    canvas.toBlob(
      (blob) => { if (blob && onFrame) onFrame(blob); },
      'image/jpeg',
      0.8
    );
  }, [onFrame]);

  useEffect(() => {
    if (isRunning) {
      startWebcam();
      const startDelay = setTimeout(() => {
        intervalRef.current = setInterval(captureFrame, 1000 / fps);
      }, 1000);
      return () => {
        clearTimeout(startDelay);
        if (intervalRef.current) clearInterval(intervalRef.current);
      };
    } else {
      if (intervalRef.current) clearInterval(intervalRef.current);
      stopWebcam();
    }
  }, [isRunning, fps, captureFrame, startWebcam, stopWebcam]);

  const hasPrediction = prediction && prediction.label !== 'ERRO';

  return (
    <div className="webcam-wrap">
      {isRunning ? (
        <>
          <video ref={videoRef} autoPlay playsInline muted className="webcam-video" />
          <canvas ref={canvasRef} className="webcam-canvas" />

          <div className="live-badge">
            <span className="live-dot" />
            AO VIVO
          </div>

          {hasPrediction && (
            <div className="bounding-box">
              <span className="bounding-label">{LABELS_PT[prediction.label] || prediction.label}</span>
            </div>
          )}

          <div className="webcam-stats-bar">
            <span className="webcam-stat-chip">FPS: {currentFps}</span>
            <span className="webcam-stat-chip">Latência: {latency} ms</span>
            <span className="webcam-stat-chip">Resolução: 640x480</span>
          </div>
        </>
      ) : (
        <div className="webcam-placeholder">
          <div className="placeholder-icon">📷</div>
          <p>Clique em "Iniciar" para ativar a webcam</p>
          <button
            className="btn-start"
            onClick={onStart}
            disabled={serverStatus !== 'online'}
          >
            ▶ Iniciar
          </button>
        </div>
      )}
    </div>
  );
}

export default WebcamCapture;
