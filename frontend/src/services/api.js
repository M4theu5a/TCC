/**
 * Serviço de comunicação com a API backend.
 */

const API_BASE_URL = 'http://localhost:8000';
const TIMEOUT_MS = 5000;

/**
 * Envia um frame para o backend e recebe a predição.
 * @param {string} base64Image - Imagem em base64 (JPEG)
 * @returns {Promise<{label: string, confidence: number, latency_ms: number, dog_detected: boolean, smoothed_label: string}>}
 */
export async function predictFrame(base64Image) {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), TIMEOUT_MS);

  try {
    const response = await fetch(`${API_BASE_URL}/predict`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ image: base64Image }),
      signal: controller.signal,
    });

    clearTimeout(timeoutId);

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }

    return await response.json();
  } catch (error) {
    clearTimeout(timeoutId);

    if (error.name === 'AbortError') {
      throw new Error('Timeout: servidor demorou mais de 5 segundos');
    }

    throw error;
  }
}

/**
 * Verifica se o backend está online.
 * @returns {Promise<boolean>}
 */
export async function checkHealth() {
  try {
    const response = await fetch(`${API_BASE_URL}/health`, {
      method: 'GET',
      signal: AbortSignal.timeout(3000),
    });
    return response.ok;
  } catch {
    return false;
  }
}

/**
 * Reseta o histórico de suavização no backend.
 */
export async function resetSmoothing() {
  try {
    await fetch(`${API_BASE_URL}/reset`, { method: 'POST' });
  } catch {
    // silently ignore
  }
}
