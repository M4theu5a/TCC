/**
 * Serviço de API - Comunicação com o Backend FastAPI
 * 
 * Responsável por:
 * - Verificar saúde do servidor (/health)
 * - Enviar frames para predição (/predict)
 */

import axios from 'axios';

// URL base do backend
const API_BASE_URL = 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000, // 10 segundos de timeout
});

/**
 * Verifica se o backend está online e o modelo carregado.
 * @returns {Promise<{status: string, model_loaded: boolean, model_type: string}>}
 */
export async function checkHealth() {
  try {
    const response = await api.get('/health');
    return response.data;
  } catch (error) {
    console.error('Erro ao verificar saúde do servidor:', error);
    return { status: 'offline', model_loaded: false, model_type: 'none' };
  }
}

/**
 * Envia um frame (imagem) para o backend e recebe a predição.
 * 
 * @param {Blob} imageBlob - Blob da imagem capturada da webcam
 * @returns {Promise<{label: string, confidence: number, latency_ms: number}>}
 */
export async function predictFrame(imageBlob) {
  const formData = new FormData();
  formData.append('file', imageBlob, 'frame.jpg');

  try {
    const response = await api.post('/predict', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return response.data;
  } catch (error) {
    console.error('Erro na predição:', error);
    return {
      label: 'ERRO',
      confidence: 0,
      latency_ms: 0,
    };
  }
}

export default api;
