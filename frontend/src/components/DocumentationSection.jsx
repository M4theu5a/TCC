function DocumentationSection() {
  return (
    <div className="card section-text" style={{ maxWidth: 640 }}>
      <h2 className="card-title">Documentação</h2>
      <p>
        A documentação completa do projeto vive junto do código-fonte, no
        repositório Git — este app não replica esses arquivos, apenas
        aponta para onde encontrá-los:
      </p>
      <ul>
        <li><code>README.md</code> — visão geral, arquitetura e como executar</li>
        <li><code>SETUP.md</code> — guia passo a passo de instalação</li>
        <li><code>docs/tcc/</code> — documentação acadêmica: metodologia, dataset, resultados e referências</li>
        <li><code>docs/diagramas/</code> — diagramas de arquitetura</li>
      </ul>
      <p style={{ marginTop: 14 }}>
        A seção <strong>Métricas</strong> deste app já traz os resultados
        (acurácia, F1 por classe, matriz de confusão) diretamente da última
        avaliação do modelo.
      </p>
    </div>
  );
}

export default DocumentationSection;
