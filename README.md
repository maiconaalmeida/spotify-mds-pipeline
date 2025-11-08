# Pipeline de Analytics em Tempo Real do Spotify

![Snowflake](https://img.shields.io/badge/Snowflake-29B5E8?logo=snowflake&logoColor=white)
![DBT](https://img.shields.io/badge/dbt-FF694B?logo=dbt&logoColor=white)
![Apache Airflow](https://img.shields.io/badge/Apache%20Airflow-017CEE?logo=apacheairflow&logoColor=white)
![Apache Kafka](https://img.shields.io/badge/Apache%20Kafka-231F20?logo=apachekafka&logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB?logo=python&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2496ED?logo=docker&logoColor=white)
![Power BI](https://img.shields.io/badge/Power%20BI-F2C811?logo=powerbi&logoColor=black)
![Modern Data Stack](https://img.shields.io/badge/Modern%20Data%20Stack-00C7B7?logo=databricks&logoColor=white)
---

Pipeline de dados completo end-to-end para analytics de streaming do Spotify usando Modern Data Stack
Funcionalidades • Arquitetura • Início Rápido • Documentação • Contribuindo
🎯 Visão Geral
Este projeto implementa um pipeline de dados em tempo real de nível produção para analytics de streaming de música do Spotify, demonstrando as melhores práticas de engenharia de dados moderna. O pipeline simula milhões de eventos de streaming, processa-os em tempo real e entrega insights acionáveis através de dashboards interativos.
O Que Torna Este Projeto Especial?

🚀 Totalmente Automatizado: Uma vez iniciado, o pipeline roda de forma autônoma ponta a ponta
⚡ Processamento em Tempo Real: Latência inferior a um segundo desde geração até visualização
🏗️ Pronto para Produção: Implementa padrões e práticas da indústria
📦 100% Containerizado: Deploy com um único comando usando Docker Compose
🔄 Arquitetura Medallion: Camadas de dados Bronze → Silver → Gold
✅ Qualidade em Primeiro Lugar: Testes e validações integrados em cada etapa

Valor de Negócio
Este pipeline responde questões críticas de negócio:

📊 Quais músicas estão em alta agora?
🌍 Quais regiões têm maior engajamento?
📱 Como os usuários consomem conteúdo em diferentes dispositivos?
⏰ Quais são os horários de pico de escuta?
🎭 Quais gêneros estão ganhando popularidade?

---
✨ Funcionalidades
Capacidades Principais

Streaming em Tempo Real: Apache Kafka processa milhões de eventos por segundo
Armazenamento Escalável: MinIO fornece armazenamento de objetos compatível com S3
Data Warehouse em Nuvem: Snowflake permite analytics em escala de petabytes
Transformação de Dados: dbt garante modelos de dados limpos, testados e documentados
Orquestração de Workflows: Airflow gerencia dependências complexas e agendamentos
Dashboards Interativos: Power BI entrega insights aos stakeholders

Melhores Práticas de Engenharia de Dados

✅ Arquitetura Medallion (Bronze/Silver/Gold)
✅ Processamento Incremental (apenas dados novos)
✅ Testes de Qualidade de Dados (dbt tests)
✅ Validação de Schema (verificações automatizadas)
✅ Pipelines Idempotentes (execuções seguras)
✅ Rastreamento de Linhagem (proveniência dos dados)
✅ Documentação como Código (dbt docs)
---

🏗️ Arquitetura
Diagrama de Arquitetura de Alto Nível
┌──────────────────────────────────────────────────────────────────────┐
│                         GERAÇÃO DE DADOS                              │
│  ┌────────────────────────────────────────────────────────────┐     │
│  │  Simulador Python (Faker)                                   │     │
│  │  • Gera eventos realistas de streaming                      │     │
│  │  • ~1000 eventos/segundo                                    │     │
│  │  • Simulação multi-região e multi-dispositivo               │     │
│  └─────────────────────────┬────────────────────────────────────┘   │
└────────────────────────────┼─────────────────────────────────────────┘
                             │
                             ▼
┌──────────────────────────────────────────────────────────────────────┐
│                      STREAMING EM TEMPO REAL                          │
│  ┌────────────────────────────────────────────────────────────┐     │
│  │  Apache Kafka                                               │     │
│  │  • Tópico: spotify_plays                                    │     │
│  │  • Partições: 3                                             │     │
│  │  • Retenção: 7 dias                                         │     │
│  └─────────────────────────┬────────────────────────────────────┘   │
└────────────────────────────┼─────────────────────────────────────────┘
                             │
                             ▼
┌──────────────────────────────────────────────────────────────────────┐
│                       DATA LAKE (BRUTO)                               │
│  ┌────────────────────────────────────────────────────────────┐     │
│  │  MinIO (Compatível com S3)                                  │     │
│  │  • Bucket: spotify-raw-data                                 │     │
│  │  • Formato: JSON (particionado por data)                    │     │
│  │  • Caminho: /ano/mes/dia/hora/                             │     │
│  └─────────────────────────┬────────────────────────────────────┘   │
└────────────────────────────┼─────────────────────────────────────────┘
                             │
                             ▼
┌──────────────────────────────────────────────────────────────────────┐
│                    CAMADA DE ORQUESTRAÇÃO                             │
│  ┌────────────────────────────────────────────────────────────┐     │
│  │  Apache Airflow                                             │     │
│  │  ┌──────────────────────────────────────────────────────┐ │     │
│  │  │ DAG 1: spotify_ingestion_pipeline                    │ │     │
│  │  │ • Extrai do MinIO                                    │ │     │
│  │  │ • Carrega no Snowflake Bronze                        │ │     │
│  │  │ • Agendamento: A cada 5 minutos                      │ │     │
│  │  └──────────────────────────────────────────────────────┘ │     │
│  │  ┌──────────────────────────────────────────────────────┐ │     │
│  │  │ DAG 2: spotify_transformation_pipeline               │ │     │
│  │  │ • Dispara transformações dbt                         │ │     │
│  │  │ • Bronze → Silver → Gold                             │ │     │
│  │  │ • Agendamento: A cada 10 minutos                     │ │     │
│  │  └──────────────────────────────────────────────────────┘ │     │
│  └─────────────────────────┬────────────────────────────────────┘   │
└────────────────────────────┼─────────────────────────────────────────┘
                             │
                             ▼
┌──────────────────────────────────────────────────────────────────────┐
│                   DATA WAREHOUSE (SNOWFLAKE)                          │
│  ┌────────────────────────────────────────────────────────────┐     │
│  │  🥉 CAMADA BRONZE (Bruto)                                   │     │
│  │  • RAW_PLAYS (coluna VARIANT com JSON completo)            │     │
│  │  • Sem transformações aplicadas                            │     │
│  └─────────────────────────┬────────────────────────────────────┘   │
│                            │                                          │
│  ┌────────────────────────▼────────────────────────────────────┐   │
│  │  🥈 CAMADA SILVER (Limpo e Padronizado)                     │     │
│  │  • STG_PLAYS: Dados de reproduções limpos                   │     │
│  │  • STG_TRACKS: Músicas deduplicadas                         │     │
│  │  • STG_USERS: Usuários únicos                               │     │
│  │  • Tipos de dados validados, nulos tratados                 │     │
│  └─────────────────────────┬────────────────────────────────────┘   │
│                            │                                          │
│  ┌────────────────────────▼────────────────────────────────────┐   │
│  │  🥇 CAMADA GOLD (Marts de Negócio)                          │     │
│  │  • FCT_PLAYS: Tabela fato (eventos de streaming)            │     │
│  │  • DIM_TRACKS: Dimensão de músicas                          │     │
│  │  • DIM_ARTISTS: Dimensão de artistas                        │     │
│  │  • DIM_REGIONS: Dimensão geográfica                         │     │
│  │  • DIM_TIME: Dimensão temporal                              │     │
│  └─────────────────────────┬────────────────────────────────────┘   │
└────────────────────────────┼─────────────────────────────────────────┘
                             │
                             ▼
┌──────────────────────────────────────────────────────────────────────┐
│                    TRANSFORMAÇÃO DE DADOS (DBT)                       │
│  ┌────────────────────────────────────────────────────────────┐     │
│  │  • Transformações baseadas em SQL                           │     │
│  │  • Testes automatizados (unicidade, not_null, relacionamen.)│     │
│  │  • Geração de documentação                                  │     │
│  │  • Rastreamento de linhagem                                 │     │
│  └─────────────────────────┬────────────────────────────────────┘   │
└────────────────────────────┼─────────────────────────────────────────┘
                             │
                             ▼
┌──────────────────────────────────────────────────────────────────────┐
│                    BUSINESS INTELLIGENCE                              │
│  ┌────────────────────────────────────────────────────────────┐     │
│  │  Dashboard Power BI                                         │     │
│  │  📊 Total de Reproduções: 15,2M                             │     │
│  │  👥 Ouvintes Únicos: 892K                                   │     │
│  │  🌍 Região Top: Califórnia (2,3M reproduções)              │     │
│  │  📱 Divisão Dispositivos: 60% Mobile, 25% Desktop, 15% Web │     │
│  └──────────────────────────────────────────────────────────────┘   │
└──────────────────────────────────────────────────────────────────────┘

Fluxo de Dados Explicado

Geração: Simulador Python cria eventos realistas de streaming usando biblioteca Faker
Streaming: Producer Kafka publica eventos no tópico spotify_plays
Consumo: Consumer Kafka lê mensagens e escreve arquivos JSON no MinIO
Ingestão: DAG do Airflow copia arquivos do MinIO para camada Bronze do Snowflake
Transformação: Modelos dbt limpam, padronizam e agregam dados (Silver → Gold)
Visualização: Power BI conecta à camada Gold para dashboards em tempo real
---
🛠️ Stack Tecnológica
Infraestrutura & Orquestração

<img width="572" height="143" alt="image" src="https://github.com/user-attachments/assets/1eadc016-9711-44f4-8e35-7cf39e167e41" />

---

Streaming & Armazenamento
<img width="559" height="217" alt="image" src="https://github.com/user-attachments/assets/2c9b8c12-b0fb-45e2-b76e-3d9426ce8453" />

---
Processamento de Dados
<img width="560" height="164" alt="image" src="https://github.com/user-attachments/assets/955cac64-f5ce-485c-9420-830d1cd23484" />

---
Visualização
<img width="560" height="74" alt="image" src="https://github.com/user-attachments/assets/f9512355-7192-486f-8a17-6352feb2bfec" />

---
Bibliotecas Python
faker==19.12.0
kafka-python==2.0.2
minio==7.1.17
pandas==2.1.3
snowflake-connector-python==3.3.1
apache-airflow==2.7.3
dbt-snowflake==1.6.2
---

📁 Estrutura do Projeto
spotify-mds-pipeline/
│
├── 📁 docker/                          # Configurações Docker e Airflow
│   ├── .env                           # Variáveis de ambiente para Airflow
│   ├── docker-compose.yml             # Definição de serviços Airflow
│   ├── Dockerfile                     # Imagem customizada do Airflow
│   ├── requirements.txt               # Dependências Python do Airflow
│   │
│   └── 📁 dags/                       # DAGs do Airflow
│       ├── spotify_ingestion.py       # MinIO → Snowflake Bronze
│       ├── spotify_transformation.py  # Dispara execuções dbt
│       ├── utils/                     # Utilitários compartilhados
│       │   ├── snowflake_conn.py     # Helper de conexão Snowflake
│       │   └── slack_alerts.py       # Sistema de notificações
│       └── .env                       # Variáveis específicas das DAGs
│
├── 📁 simulator/                       # Serviço de geração de dados
│   ├── producer.py                    # Producer Kafka (gera eventos)
│   ├── schemas.py                     # Schemas e validação de dados
│   ├── config.py                      # Gerenciamento de configuração
│   ├── Dockerfile                     # Container do simulador
│   ├── requirements.txt               # Dependências Python
│   └── .env                           # Variáveis de ambiente do producer
│
├── 📁 consumer/                        # Serviço consumer Kafka
│   ├── kafka_to_minio.py             # Consome do Kafka → MinIO
│   ├── config.py                      # Configuração do consumer
│   ├── Dockerfile                     # Container do consumer
│   ├── requirements.txt               # Dependências Python
│   └── .env                           # Variáveis de ambiente do consumer
│
├── 📁 spotify_dbt/                     # Projeto dbt
│   ├── dbt_project.yml                # Configuração do projeto dbt
│   ├── profiles.yml                   # Perfis de conexão Snowflake
│   ├── packages.yml                   # Pacotes dbt (dbt_utils, etc.)
│   │
│   ├── 📁 models/                     # Modelos dbt
│   │   ├── sources.yml                # Definições de fontes (camada Bronze)
│   │   │
│   │   ├── 📁 staging/                # Camada Silver (dados limpos)
│   │   │   ├── stg_plays.sql         # Staging: eventos de reprodução
│   │   │   ├── stg_tracks.sql        # Staging: metadados de músicas
│   │   │   ├── stg_users.sql         # Staging: usuários
│   │   │   ├── stg_regions.sql       # Staging: dados geográficos
│   │   │   └── schema.yml            # Testes e documentação
│   │   │
│   │   ├── 📁 intermediate/           # Transformações intermediárias
│   │   │   ├── int_plays_enriched.sql # Reproduções com info de músicas
│   │   │   └── int_user_metrics.sql   # Agregações por usuário
│   │   │
│   │   └── 📁 marts/                  # Camada Gold (marts de negócio)
│   │       ├── 📁 core/
│   │       │   ├── fct_plays.sql     # Fato: eventos de streaming
│   │       │   ├── dim_tracks.sql    # Dimensão: músicas
│   │       │   ├── dim_artists.sql   # Dimensão: artistas
│   │       │   ├── dim_regions.sql   # Dimensão: regiões
│   │       │   ├── dim_devices.sql   # Dimensão: dispositivos
│   │       │   └── dim_time.sql      # Dimensão: tempo
│   │       │
│   │       └── 📁 analytics/
│   │           ├── top_tracks_daily.sql      # Top músicas diárias
│   │           ├── regional_trends.sql       # Analytics regionais
│   │           └── user_engagement.sql       # Métricas de comportamento
│   │
│   ├── 📁 macros/                     # Macros customizados dbt
│   │   ├── generate_schema_name.sql   # Lógica de nomeação de schemas
│   │   └── custom_tests.sql           # Testes customizados de qualidade
│   │
│   ├── 📁 tests/                      # Testes customizados de dados
│   │   └── assert_positive_plays.sql  # Validações de regras de negócio
│   │
│   └── 📁 snapshots/                  # Dimensões de mudança lenta
│       └── scd_tracks.sql             # Snapshots de histórico de músicas
│
├── 📁 dashboards/                      # Relatórios Power BI
│   ├── spotify_analytics.pbix         # Arquivo principal do dashboard
│   ├── queries/                       # Queries DAX customizadas
│   └── screenshots/                   # Imagens de preview do dashboard
│
├── 📁 infrastructure/                  # Infraestrutura como Código (opcional)
│   ├── terraform/                     # Configurações Terraform
│   │   ├── main.tf                   # Infraestrutura principal
│   │   ├── snowflake.tf              # Recursos Snowflake
│   │   └── variables.tf              # Variáveis
│   └── scripts/                       # Scripts de setup
│       ├── setup_snowflake.sql       # Inicialização Snowflake
│       └── create_buckets.sh         # Criação de buckets MinIO
│
├── 📁 tests/                           # Testes da aplicação
│   ├── unit/                          # Testes unitários
│   ├── integration/                   # Testes de integração
│   └── fixtures/                      # Dados de teste
│
├── 📁 docs/                            # Documentação
│   ├── ARCHITECTURE.md                # Documentação detalhada da arquitetura
│   ├── DATA_MODEL.md                  # Documentação do modelo de dados
│   ├── SETUP.md                       # Guia de setup
│   ├── TROUBLESHOOTING.md             # Problemas comuns
│   └── images/                        # Diagramas de arquitetura
│
├── .env.example                        # Exemplo de variáveis de ambiente
├── .gitignore                          # Padrões de ignore do Git
├── docker-compose.yml                  # Arquivo principal de orquestração
├── Makefile                            # Comandos de conveniência
├── requirements.txt                    # Dependências Python raiz
├── README.md                           # Este arquivo
└── LICENSE                             # Licença do projeto

---
🔧 Pré-requisitos
Software Necessário

Docker Desktop (4.20+) - Download
Docker Compose (2.20+) - Incluído no Docker Desktop
Git - Download
Conta Snowflake - Cadastre-se para teste grátis
Power BI Desktop (opcional) - Download

---

Requisitos de Sistema
<img width="562" height="164" alt="image" src="https://github.com/user-attachments/assets/e97ff0d5-e1df-4f94-96f0-b04a9d41d6ff" />

---
Requisitos de Rede

Conexão com internet para imagens Docker e Snowflake
Portas disponíveis: 8080 (Airflow), 9092 (Kafka), 9000-9001 (MinIO), 2181 (Zookeeper)

---
🚀 Instalação
1. Clone o Repositório
   git clone https://github.com/maiconaalmeida/spotify-mds-pipeline.git
cd spotify-mds-pipeline
---

2. Configure as Variáveis de Ambiente
# Copie o arquivo de exemplo
cp .env.example .env

# Edite o arquivo .env com suas credenciais
nano .env  # ou vim, code, etc.
---

Variáveis Obrigatórias:
# Configuração Snowflake
SNOWFLAKE_ACCOUNT=seu_identificador_conta
SNOWFLAKE_USER=seu_usuario
SNOWFLAKE_PASSWORD=sua_senha
SNOWFLAKE_WAREHOUSE=COMPUTE_WH
SNOWFLAKE_DATABASE=SPOTIFY_DB
SNOWFLAKE_SCHEMA=BRONZE
SNOWFLAKE_ROLE=ACCOUNTADMIN

# Configuração MinIO
MINIO_ROOT_USER=admin
MINIO_ROOT_PASSWORD=senha_admin_minio
MINIO_BUCKET_NAME=spotify-raw-data

# Configuração Kafka
KAFKA_BROKER=kafka:9092
KAFKA_TOPIC=spotify_plays

# Configuração Airflow
AIRFLOW_UID=50000
AIRFLOW__CORE__FERNET_KEY=sua_chave_fernet_aqui

---
3. Inicialize o Snowflake
Execute o script de setup para criar bancos de dados, schemas e tabelas:
# Conecte ao Snowflake e execute
./infrastructure/scripts/setup_snowflake.sql

Ou execute manualmente:
-- Criar banco de dados e schemas
CREATE DATABASE IF NOT EXISTS SPOTIFY_DB;

CREATE SCHEMA IF NOT EXISTS SPOTIFY_DB.BRONZE;
CREATE SCHEMA IF NOT EXISTS SPOTIFY_DB.SILVER;
CREATE SCHEMA IF NOT EXISTS SPOTIFY_DB.GOLD;

-- Criar tabela da camada Bronze
CREATE TABLE IF NOT EXISTS SPOTIFY_DB.BRONZE.RAW_PLAYS (
    raw_data VARIANT,
    load_timestamp TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    source_file STRING,
    _metadata VARIANT
);

-- Criar formato de arquivo para JSON
CREATE FILE FORMAT IF NOT EXISTS SPOTIFY_DB.BRONZE.JSON_FORMAT
    TYPE = 'JSON'
    COMPRESSION = 'AUTO'
    STRIP_OUTER_ARRAY = TRUE;

-- Criar warehouse (se não existir)
CREATE WAREHOUSE IF NOT EXISTS COMPUTE_WH
    WAREHOUSE_SIZE = 'XSMALL'
    AUTO_SUSPEND = 60
    AUTO_RESUME = TRUE;
---
4. Construa e Inicie os Serviços
   # Construir todas as imagens Docker
docker-compose build

# Iniciar todos os serviços em modo detached
docker-compose up -d

# Verificar status dos serviços
docker-compose ps

Saída Esperada:
NOME                    STATUS              PORTAS
kafka                   running             0.0.0.0:9092->9092/tcp
zookeeper               running             0.0.0.0:2181->2181/tcp
minio                   running             0.0.0.0:9000-9001->9000-9001/tcp
airflow-webserver       running             0.0.0.0:8080->8080/tcp
airflow-scheduler       running
producer                running
consumer                running

---
5. Acesse os Serviços
   <img width="555" height="178" alt="image" src="https://github.com/user-attachments/assets/f42ef2f2-79c0-4b01-8dec-5ac43cf07ff5" />

---
6. Verifique a Instalação
# Verificar logs do Airflow
docker-compose logs -f airflow-webserver

# Verificar tópicos Kafka
docker-compose exec kafka kafka-topics --list --bootstrap-server localhost:9092

# Verificar buckets MinIO
docker-compose exec minio mc ls minio/

# Testar conexão Snowflake
docker-compose exec airflow-webserver airflow connections test snowflake_default

---
⚙️ Configuração
Conexões do Airflow
Configure a conexão Snowflake na UI do Airflow:

Navegue até Admin → Connections
Clique em + para adicionar nova conexão
Preencha os detalhes:

Connection Id: snowflake_default
Connection Type: Snowflake
Account: seu_identificador_conta
Warehouse: COMPUTE_WH
Database: SPOTIFY_DB
Role: ACCOUNTADMIN
Login: seu_usuario
Password: sua_senha

---
Perfil dbt
Edite spotify_dbt/profiles.yml:
spotify_dbt:
  outputs:
    dev:
      type: snowflake
      account: "{{ env_var('SNOWFLAKE_ACCOUNT') }}"
      user: "{{ env_var('SNOWFLAKE_USER') }}"
      password: "{{ env_var('SNOWFLAKE_PASSWORD') }}"
      role: ACCOUNTADMIN
      database: SPOTIFY_DB
      warehouse: COMPUTE_WH
      schema: SILVER
      threads: 4
      client_session_keep_alive: False
    
    prod:
      type: snowflake
      account: "{{ env_var('SNOWFLAKE_ACCOUNT') }}"
      user: "{{ env_var('SNOWFLAKE_USER') }}"
      password: "{{ env_var('SNOWFLAKE_PASSWORD') }}"
      role: ACCOUNTADMIN
      database: SPOTIFY_DB
      warehouse: COMPUTE_WH
      schema: GOLD
      threads: 8
      client_session_keep_alive: False
  
  target: dev

  ---
  Configuração de Tópicos Kafka
Ajuste partições e replicação:
docker-compose exec kafka kafka-topics \
  --create \
  --topic spotify_plays \
  --bootstrap-server localhost:9092 \
  --partitions 3 \
  --replication-factor 1 \
  --config retention.ms=604800000  # 7 dias

  ---
  🎮 Como Usar
Iniciando o Pipeline
# Iniciar todos os serviços
make start

# Ou usando docker-compose
docker-compose up -d

---
Monitoramento
Ver Logs:
# Todos os serviços
docker-compose logs -f

# Serviço específico
docker-compose logs -f producer
docker-compose logs -f consumer
docker-compose logs -f airflow-scheduler

---
# Todos os serviços
docker-compose logs -f

# Serviço específico
docker-compose logs -f producer
docker-compose logs -f consumer
docker-compose logs -f airflow-scheduler

---
UI do Airflow:

Abra http://localhost:8080
Habilite as DAGs: spotify_ingestion_pipeline e spotify_transformation_pipeline
Monitore a execução das tasks na visualização Graph ou Tree

Console MinIO:

Abra http://localhost:9001
Navegue no bucket spotify-raw-data
Verifique se arquivos JSON estão sendo criados

Executando dbt Manualmente
---

# Entrar no container Airflow
docker-compose exec airflow-webserver bash

# Navegar para o projeto dbt
cd /opt/dbt/spotify_dbt

# Executar todos os modelos
dbt run

# Executar modelos específicos
dbt run --models

