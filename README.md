🎧 Spotify MDS Pipeline

Pipeline de dados para extração, transformação e carga (ETL/ELT) de informações do Spotify, desenvolvido com foco em boas práticas de engenharia de dados e automação de processos.

📘 Sumário
- Visão Geral
- Arquitetura do Projeto
- Tecnologias Utilizadas
- Instalação e Execução
- Estrutura de Pastas
- Fluxo do Pipeline
- Melhorias Futuras
- Autor

🧠 Visão Geral
Este projeto tem como objetivo coletar dados do Spotify (via API), processá-los e armazená-los em um modelo de dados simplificado (MDS – Model Data Simplified).
O foco é demonstrar o fluxo completo de engenharia de dados: da extração bruta até o modelo pronto para análise.

🏗️ Arquitetura do Projeto
Spotify API -> Extract -> Transform -> Load -> Dashboard

🧰 Tecnologias Utilizadas
- Python 3.10+
- Requests – integração com a API do Spotify
- Pandas – tratamento e modelagem dos dados
- Docker – containerização do pipeline
- Airflow (opcional) – orquestração do fluxo
- SQLite / CSV – armazenamento de dados

⚙️ Instalação e Execução
1. Clonar o repositório:
   git clone https://github.com/maiconaalmeida/spotify-mds-pipeline.git
   cd spotify-mds-pipeline

2. Criar ambiente virtual:
   python -m venv .venv
   source .venv/bin/activate  (Linux / Mac)
   .venv\Scripts\activate   (Windows)

3. Instalar dependências:
   pip install -r requirements.txt

4. Executar o pipeline:
   python src/main.py

📂 Estrutura de Pastas
spotify-mds-pipeline/
│
├── src/
│   ├── extract/         # Scripts de extração da API
│   ├── transform/       # Limpeza e transformação
│   ├── load/            # Carga e persistência
│   └── main.py          # Ponto de entrada
│
├── data/
│   ├── raw/             # Dados brutos
│   ├── processed/       # Dados transformados
│   └── outputs/         # Relatórios ou modelos finais
│
├── tests/               # Testes unitários
├── docker-compose.yml   # Orquestração (opcional)
├── requirements.txt
├── .gitignore
└── README.md

🔄 Fluxo do Pipeline
1. Extração: coleta de dados de artistas, músicas e playlists via API do Spotify.
2. Transformação: limpeza, padronização e enriquecimento dos dados.
3. Carga: armazenamento em formato CSV ou banco SQLite para posterior análise.



👨‍💻 Autor
Maicon Almeida
Engenheiro de Dados
LinkedIn: https://www.linkedin.com/in/maiconaalmeida
