/**
 * Componente WebcamCapture
 * 
 * Responsável por:
 * - Acessar a webcam do usuário (getUserMedia)
 * - Capturar frames via canvas
 * - Converter frames para Blob (JPEG)
 * - Enviar para a API em intervalos regulares
 */

import { useRef, useEffect, useCallback } from 'react';

/**
 * @param {Object} props
 * @param {boolean} props.isRunning - Se está capturando frames
 * @param {function} props.onFrame - Callback chamado com o Blob de cada frame
 * @param {number} props.fps - Frames por segundo desejados (padrão: 5)
 * @param {Object|null} props.prediction - Última predição recebida
 */
function WebcamCapture({ isRunning, onFrame, fps = 5, prediction }) {
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const streamRef = useRef(null);
  const intervalRef = useRef(null);

  // Inicia a webcam
  const startWebcam = useCallback(async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: {
          width: { ideal: 640 },
          height: { ideal: 480 },
          facingMode: 'user',
        },
      });

      streamRef.current = stream;

      if (videoRef.current) {
        videoRef.current.srcObject = stream;
      }
    } catch (error) {
      console.error('Erro ao acessar webcam:', error);
      alert(
        'Não foi possível acessar a webcam. Verifique as permissões do navegador.'
      );
    }
  }, []);

  // Para a webcam
  const stopWebcam = useCallback(() => {
    if (streamRef.current) {
      streamRef.current.getTracks().forEach((track) => track.stop());
      streamRef.current = null;
    }
    if (videoRef.current) {
      videoRef.current.srcObject = null;
    }
  }, []);

  // Captura um frame e envia como Blob
  const captureFrame = useCallback(() => {
    const video = videoRef.current;
    const canvas = canvasRef.current;

    if (!video || !canvas || video.readyState < 2) return;

    const ctx = canvas.getContext('2d');
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;

    // Desenha o frame atual no canvas
    ctx.drawImage(video, 0, 0);

    // Converte para Blob JPEG e chama o callback
    canvas.toBlob(
      (blob) => {
        if (blob && onFrame) {
          onFrame(blob);
        }
      },
      'image/jpeg',
      0.8 // qualidade 80%
    );
  }, [onFrame]);

  // Gerencia o loop de captura
  useEffect(() => {
    if (isRunning) {
      startWebcam();
      // Aguarda a webcam iniciar antes de começar a capturar
      const startDelay = setTimeout(() => {
        intervalRef.current = setInterval(captureFrame, 1000 / fps);
      }, 1000);

      return () => {
        clearTimeout(startDelay);
        if (intervalRef.current) {
          clearInterval(intervalRef.current);
        }
      };
    } else {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
      stopWebcam();
    }
  }, [isRunning, fps, captureFrame, startWebcam, stopWebcam]);

  // Labels amigáveis
  const labelMap = {
    EM_PE: '🐕 Em Pé',
    SENTADO: '🐕 Sentado',
    DEITADO: '🐕 Deitado',
    ERRO: '❌ Erro',
  };

  return (
    <div className="webcam-section">
      {isRunning ? (
        <>
          <video
            ref={videoRef}
            autoPlay
            playsInline
            muted
            className="webcam-video"
          />
          <canvas ref={canvasRef} className="webcam-canvas" />

          {/* Overlay com a predição */}
          {prediction && prediction.label !== 'ERRO' && (
            <div className="prediction-overlay">
              <div className={`prediction-label ${prediction.label}`}>
                {labelMap[prediction.label] || prediction.label}
              </div>
              <div className="prediction-confidence">
                Confiança: {(prediction.confidence * 100).toFixed(1)}%
              </div>
            </div>
          )}
        </>
      ) : (
        <div className="webcam-placeholder">
          <span>📷</span>
          <p>Clique em "Iniciar" para ativar a webcam</p>
        </div>
      )}
    </div>
  );
}

export default WebcamCapture;
