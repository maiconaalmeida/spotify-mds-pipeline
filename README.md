# Pipeline MDS Spotify

Este repositório contém um projeto exemplo que implementa um pipeline Modern Data Stack (MDS) para coletar, processar e disponibilizar dados do Spotify para análise. O objetivo deste README é explicar, de forma clara e didática, o propósito do projeto, as tecnologias e metodologias utilizadas e orientar passo a passo — como se você fosse um estudante do primeiro semestre, sem experiência prévia — para executar o projeto localmente.

Sumário
- O que este projeto faz
- Conceitos básicos (API, ETL, MDS)
- Tecnologias e por que foram escolhidas
- Pré-requisitos (com instruções detalhadas)
- Passo a passo: rodando localmente (modo “sem Docker”)
- Passo a passo: rodando com Docker (recomendado)
- Arquivos e estrutura do projeto
- Como obter credenciais do Spotify
- Verificação e solução de problemas comuns
- Como contribuir
- Licença

O que este projeto faz
- Extrai dados da API do Spotify (por exemplo, informações de músicas, artistas e playlists).
- Processa e transforma esses dados (limpeza, validação e modelagem).
- Carrega os dados em um banco de dados (data warehouse PostgreSQL) para consultas e análises.
- Orquestra e automatiza as etapas com Airflow.
- Aplica verificações de qualidade de dados com Great Expectations.
- Usa dbt para modelagem/transformação analítica.

Conceitos básicos (explicação simples)
- API: é uma interface que permite pedir informações ao Spotify. Pense como ligar para um restaurante e pedir um prato.
- ETL: é o processo Extract (extrair), Transform (transformar) e Load (carregar).
- MDS (Modern Data Stack): conjunto de ferramentas modernas para coletar, transformar e analisar dados (ex.: Airflow, dbt, Great Expectations, warehouse).
- Orquestração: agendar e gerenciar tarefas (Airflow faz isso).
- Data Warehouse: banco de dados otimizado para análises (usamos PostgreSQL aqui de forma didática).

Tecnologias usadas e papel no projeto
- Python 3.9+: linguagem principal que contém scripts e lógica.
- Docker & Docker Compose: encapsulam serviços (Airflow, PostgreSQL) para rodar facilmente sem instalar tudo manualmente.
- Airflow: orquestra pipelines (executa as etapas na ordem correta e registra histórico).
- dbt: modela dados (transformações SQL versionadas).
- PostgreSQL: armazena dados processados.
- Great Expectations: valida qualidade dos dados após transformações.
- Spotify Web API: fonte dos dados.

Pré-requisitos (o que instalar antes)
- Computador com Windows, macOS ou Linux.
- Internet (para baixar imagens Docker e acessar API do Spotify).
- Git (para clonar o repositório).
- Docker Desktop (recomendado: instalar e ativar).
- Python 3.9+ (se optar por rodar sem Docker).
- Conta de desenvolvedor Spotify (para obter client id e client secret).

Instalação passo a passo (do absoluto zero)

1) Abrir o terminal / prompt de comando
- Windows: abra o PowerShell ou Prompt de Comando. Sugestão: use o Windows Terminal.
- macOS / Linux: abra o Terminal.

2) Clonar o repositório
```bash
git clone https://github.com/seunome/spotify-mds-pipeline.git
cd spotify-mds-pipeline
```

3) Criar credenciais do Spotify
- Vá até https://developer.spotify.com/dashboard/
- Faça login com sua conta Spotify (ou crie uma).
- Crie uma nova aplicação (Create an App).
- Copie o Client ID e Client Secret.

4) Criar arquivo .env no diretório do projeto
- Crie um arquivo chamado `.env` e cole:
```env
SPOTIFY_CLIENT_ID=seu_client_id_aqui
SPOTIFY_CLIENT_SECRET=seu_client_secret_aqui
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=spotify_db
```
- Substitua os valores de Spotify pelos que obteve no dashboard.

Como rodar (opção A: recomendado — Docker Compose)
- Vantagens: todos os serviços (Postgres, Airflow, web UI do dbt) ficam prontos sem instalar manualmente.

1. Certifique-se de ter o Docker Desktop em execução.
2. No diretório do projeto:
```bash
docker-compose build
docker-compose up -d
```
3. Verifique os serviços:
```bash
docker-compose ps
```
4. Acesse as interfaces:
- Airflow: http://localhost:8080 (user: airflow / password: airflow — caso o projeto já tenha credenciais pré-configuradas)
- dbt docs (se configurado): http://localhost:8081
- PostgreSQL: host=localhost port=5432 (use um cliente SQL como DBeaver ou pgAdmin)

5. Trigger do pipeline
- Você pode acionar o DAG (pipeline) pelo Airflow UI: procure o DAG principal e clique em “Trigger DAG”.
- Ou executar scripts localmente (veja abaixo).

Como rodar (opção B: sem Docker — para aprendizado)
- Requer Python 3.9+ instalado.

1. Criar e ativar um ambiente virtual (opcional, recomendado)
```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate
```
2. Instalar dependências
```bash
pip install -r requirements.txt
```
3. Verificar sistema (se houver script)
```bash
python system_check.py
```
4. Rodar o script principal (exemplo simples)
```bash
python main.py
```
- main.py deve usar as variáveis do `.env` para autenticar na API do Spotify e iniciar o fluxo de ETL.

O que esperar ao executar
- Ao rodar com Docker: verá containers iniciando. Após iniciar, abra o Airflow UI e acione o DAG. Os logs mostrarão cada etapa: extração, transformação, validação e carga.
- Ao rodar localmente: o console exibirá logs das etapas e possíveis erros (como falha de autenticação com Spotify).

Estrutura do projeto (explicação dos diretórios)
```
spotify-mds-pipeline/
├── docker/                 # configurações Docker e imagens customizadas
├── dbt/                    # projetos dbt: modelos SQL, seeds, docs
├── airflow/                # DAGs, operators e configurações do Airflow
├── tests/                  # testes unitários e integração
├── system_check.py         # script para validar ambiente
├── main.py                 # script principal de demonstração / execução do pipeline
├── requirements.txt        # dependências Python
├── docker-compose.yml      # orquestração local dos serviços
└── .env.example            # exemplo de variáveis de ambiente
```

Metodologias aplicadas
- MDS (Modern Data Stack): separação de responsabilidades (ingestão, armazenamento, transformação).
- Testes e qualidade: Great Expectations para validar suposições dos dados (ex.: colunas não nulas, intervalo de valores).
- Versionamento e reproducibilidade: dbt para transformar dados de forma reprodutível e documentada.
- Observabilidade: Airflow provê histórico e logs para depuração.

Dicas e solução de problemas
- Erro de autenticação Spotify: verifique se SPOTIFY_CLIENT_ID e SPOTIFY_CLIENT_SECRET estão corretos e salvos no `.env`.
- Porta já em uso (ex.: 8080 ou 5432): pare o serviço que usa a porta ou altere portas no docker-compose.yml.
- Docker não inicia containers: verifique logs:
```bash
docker-compose logs -f
```
- Conexão com PostgreSQL falha: assegure-se de que o container do PostgreSQL está em execução e as credenciais batem com o `.env`.

Testes e verificação de qualidade
- Rode os testes (se existirem):
```bash
pytest -q
```
- Rode as verificações do Great Expectations via dbt / scripts configurados (consulte dbt/ e airflow/ para integrações).

Como contribuir (passos simples)
1. Faça um fork do repositório no GitHub.
2. Crie uma branch com sua feature: git checkout -b feat/minha-feature
3. Faça commits claros e pequenos.
4. Abra um Pull Request descrevendo a mudança.
5. Responda a feedbacks e atualize o PR.

Recursos úteis para iniciantes
- Git: https://git-scm.com/book/pt-br/v2
- Docker: https://docs.docker.com/get-started/
- Python: https://docs.python.org/pt-br/3/tutorial/index.html
- Spotify Developer: https://developer.spotify.com/documentation/web-api/

Licença
- Projeto licenciado sob a Licença MIT. Consulte o arquivo LICENSE no repositório para detalhes.

Contatos e próximos passos
- Para dúvidas, abra uma Issue no repositório.
- Sugestão de próximos passos para estudos: entender APIs REST, estudar SQL básico, experimentar queries no PostgreSQL e estudar DAGs simples no Airflow.

Boa sorte — siga os passos com calma, verifique logs quando algo não funcionar e divida o problema em partes pequenas (extrair → transformar → carregar).

⭐ Se você acha que este projeto merece, dê uma estrela. 