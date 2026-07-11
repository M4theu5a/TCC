import { useEffect, useState } from "react";
import { getMetrics } from "../services/api";

const LABELS_PT = {
  EM_PE: "Em Pé",
  SENTADO: "Sentado",
  DEITADO: "Deitado",
};

function MetricsSection() {
  const [metrics, setMetrics] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getMetrics().then((data) => {
      setMetrics(data);
      setLoading(false);
    });
  }, []);

  if (loading) {
    return (
      <div className="card">
        <h2 className="card-title">Métricas do Modelo</h2>
        <p className="metrics-empty">Carregando...</p>
      </div>
    );
  }

  if (!metrics || !metrics.available) {
    return (
      <div className="card">
        <h2 className="card-title">Métricas do Modelo</h2>
        <p className="metrics-empty">
          Nenhuma métrica disponível ainda. Rode o pipeline de treino
          (<code>backend/training/train.py</code> e{" "}
          <code>backend/training/evaluate.py</code>) para gerar a avaliação
          do modelo no conjunto de teste.
        </p>
      </div>
    );
  }

  const { classes, accuracy, per_class, macro_avg_f1, mean_latency_ms, effective_fps, test_set_size, confusion_matrix } = metrics;

  return (
    <div className="section-grid">
      <div className="card">
        <h2 className="card-title">Desempenho no Conjunto de Teste</h2>
        <table className="stat-table">
          <tbody>
            <tr>
              <td>Acurácia</td>
              <td>{(accuracy * 100).toFixed(1)}%</td>
            </tr>
            <tr>
              <td>F1-score (macro)</td>
              <td>{(macro_avg_f1 * 100).toFixed(1)}%</td>
            </tr>
            <tr>
              <td>Latência média</td>
              <td>{mean_latency_ms.toFixed(1)} ms</td>
            </tr>
            <tr>
              <td>FPS efetivo</td>
              <td>{effective_fps.toFixed(1)}</td>
            </tr>
            <tr>
              <td>Tamanho do conjunto de teste</td>
              <td>{test_set_size} imagens</td>
            </tr>
          </tbody>
        </table>

        <h2 className="card-title" style={{ marginTop: 18 }}>Por Classe</h2>
        <table className="stat-table">
          <thead>
            <tr>
              <th>Classe</th>
              <th>Precisão</th>
              <th>Recall</th>
              <th>F1</th>
            </tr>
          </thead>
          <tbody>
            {classes.map((cls) => (
              <tr key={cls}>
                <td>{LABELS_PT[cls] || cls}</td>
                <td>{(per_class[cls].precision * 100).toFixed(1)}%</td>
                <td>{(per_class[cls].recall * 100).toFixed(1)}%</td>
                <td>{(per_class[cls].f1_score * 100).toFixed(1)}%</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="card">
        <h2 className="card-title">Matriz de Confusão</h2>
        <table className="confusion-table">
          <thead>
            <tr>
              <th>Real \ Previsto</th>
              {classes.map((cls) => (
                <th key={cls}>{LABELS_PT[cls] || cls}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {confusion_matrix.map((row, i) => (
              <tr key={classes[i]}>
                <th>{LABELS_PT[classes[i]] || classes[i]}</th>
                {row.map((value, j) => (
                  <td key={j} className={i === j ? "diag" : undefined}>
                    {value}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

export default MetricsSection;
