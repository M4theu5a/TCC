function AboutSection() {
  return (
    <div className="section-grid">
      <div className="card section-text">
        <h2 className="card-title">Sobre o Projeto</h2>
        <p>
          Aplicação web com Inteligência Artificial capaz de reconhecer, em
          tempo real, a postura de cães a partir da webcam, classificando-os
          em três categorias: <strong>Em Pé</strong>, <strong>Sentado</strong> e{" "}
          <strong>Deitado</strong>.
        </p>
        <p>
          O sistema utiliza <strong>Transfer Learning</strong> sobre uma rede
          neural convolucional (MobileNetV2) para a classificação das
          posturas, com inferência via API REST e visualização no navegador
          em tempo real.
        </p>
        <p>
          Trabalho de Conclusão de Curso em Engenharia de Computação, com
          caráter aplicado, experimental e baseado em evidências
          quantitativas.
        </p>
      </div>

      <div className="card section-text">
        <h2 className="card-title">Stack Tecnológico</h2>
        <p>Frontend</p>
        <div className="tech-badges">
          <span className="tech-badge">React</span>
          <span className="tech-badge">Vite</span>
          <span className="tech-badge">Canvas API</span>
          <span className="tech-badge">Axios</span>
        </div>
        <p style={{ marginTop: 14 }}>Backend</p>
        <div className="tech-badges">
          <span className="tech-badge">Python 3</span>
          <span className="tech-badge">FastAPI</span>
          <span className="tech-badge">Uvicorn</span>
        </div>
        <p style={{ marginTop: 14 }}>IA / ML</p>
        <div className="tech-badges">
          <span className="tech-badge">PyTorch</span>
          <span className="tech-badge">TorchVision</span>
          <span className="tech-badge">MobileNetV2</span>
          <span className="tech-badge">Transfer Learning</span>
        </div>
        <p style={{ marginTop: 14 }}>Infraestrutura</p>
        <div className="tech-badges">
          <span className="tech-badge">Docker</span>
          <span className="tech-badge">Docker Compose</span>
        </div>
      </div>
    </div>
  );
}

export default AboutSection;
