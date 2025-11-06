🎧 Pipeline de Dados do Spotify com Modern Data Stack
https://img.shields.io/badge/Snowflake-29B5E8?logo=snowflake&logoColor=white
https://img.shields.io/badge/dbt-FF694B?logo=dbt&logoColor=white
https://img.shields.io/badge/Apache%2520Airflow-017CEE?logo=apacheairflow&logoColor=white
https://img.shields.io/badge/Apache%2520Kafka-231F20?logo=apachekafka&logoColor=white
https://img.shields.io/badge/Python-3776AB?logo=python&logoColor=white
https://img.shields.io/badge/Docker-2496ED?logo=docker&logoColor=white
https://img.shields.io/badge/Metabase-509EE3?logo=metabase&logoColor=white

📖 Sumário
🎯 Motivação do Projeto

🏗️ Arquitetura do Sistema

📋 Pré-requisitos

🚀 Instalação Rápida

🛠️ Configuração Detalhada

🔧 Como Usar

📊 Metodologia

🔍 Solução de Problemas

🤝 Contribuição

🎯 Motivação do Projeto
Este projeto nasceu da necessidade de demonstrar na prática como construir um pipeline de dados completo em produção usando tecnologias modernas. Muitos tutoriais mostram conceitos isolados, mas poucos integram todas as peças de um sistema real de dados.

Problemas que este projeto resolve:

Como ingerir dados em tempo real de forma confiável

Como transformar dados brutos em informações valiosas

Como orquestrar processos complexos de dados

Como disponibilizar insights para negócios de forma acessível

Como manter um pipeline reproduzível e versionado

Cenário de Negócio Simulado:
Imagine que você é um engenheiro de dados no Spotify precisando responder perguntas como:

Quais artistas estão em tendência por região?

Em quais horários os usuários mais ouvem música?

Como o tipo de dispositivo influencia o tempo de escuta?

Quais são os padrões de comportamento por estado brasileiro?

🏗️ Arquitetura do Sistema
Diagrama do Fluxo de Dados
text
[main.py] → [Kafka] → [MinIO] → [Airflow] → [Snowflake] → [DBT] → [Metabase]
   ↑           ↑         ↑         ↑           ↑           ↑         ↑
 Simulação   Streaming  Storage  Orquestração  DW         Transformação  Visualização
Componentes da Arquitetura
Simulação de Dados (main.py)

Gera dados realistas de streaming musical

Simula comportamentos de usuários em diferentes regiões

Produz dados em tempo real para Kafka

Streaming (Apache Kafka)

Captura eventos de reprodução em tempo real

Garante entrega confiável das mensagens

Permite consumo assíncrono dos dados

Armazenamento (MinIO)

Armazena dados brutos em formato JSON

Funciona como camada de landing zone

Compatível com Amazon S3

Orquestração (Apache Airflow)

Agenda e monitora processos de ETL

Gerencia dependências entre tarefas

Fornece observabilidade do pipeline

Data Warehouse (Snowflake)

Armazena dados nas camadas Bronze, Silver e Gold

Processa consultas complexas com performance

Escalabilidade automática

Transformação (DBT)

Aplica regras de negócio aos dados

Cria modelos dimensionais para análise

Garante qualidade dos dados com testes

Visualização (Metabase)

Dashboard interativo para análise de negócios

Consultas em tempo real

Self-service analytics

📋 Pré-requisitos
Sistema Operacional Compatível
SO	Versão	Status	Observações
Windows	10/11	✅ Compatível	Usar WSL2 recomendado
Linux	Ubuntu 18.04+	✅ Totalmente compatível	Ambiente nativo
macOS	10.15+	✅ Compatível	Intel e Apple Silicon
Requisitos de Hardware
RAM: Mínimo 8GB (16GB recomendado)

CPU: 4 cores ou mais

Armazenamento: 10GB livres

Docker: 4GB de RAM alocada

Software Necessário
Docker Desktop (Download)

Versão 20.10+

Docker Compose incluído

Python 3.8 ou superior (Download)

Pip para gerenciamento de pacotes

Git (Download)

Conta Snowflake (Free Trial)

Account URL: https://[account].snowflakecomputing.com

🚀 Instalação Rápida
1. Clonar o Projeto
bash
# Clonar o repositório
git clone https://github.com/seu-usuario/spotify-mds-pipeline.git

# Acessar o diretório
cd spotify-mds-pipeline

# Verificar estrutura do projeto
ls -la
2. Configuração Inicial
bash
# Copiar arquivos de configuração
cp docker/.env.example docker/.env
cp simulator/.env.example simulator/.env

# Instalar dependências Python
pip install -r requirements.txt
3. Execução do Pipeline
bash
# Terminal 1: Infraestrutura
docker-compose up -d

# Aguardar 2 minutos para serviços estabilizarem
sleep 120

# Terminal 2: Verificação do sistema
python check_system.py

# Terminal 3: Simulador de dados
python main.py
🛠️ Configuração Detalhada
Configuração do Snowflake
Edite o arquivo docker/.env:

env
# Configurações Snowflake
SNOWFLAKE_ACCOUNT=seu_account
SNOWFLAKE_USER=seu_usuario
SNOWFLAKE_PASSWORD=sua_senha
SNOWFLAKE_WAREHOUSE=COMPUTE_WH
SNOWFLAKE_DATABASE=SPOTIFY_ANALYTICS
SNOWFLAKE_SCHEMA=PUBLIC

# Configurações Kafka
KAFKA_BOOTSTRAP_SERVERS=kafka:9092
KAFKA_TOPIC=spotify-plays

# Configurações MinIO
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin
MINIO_BUCKET=spotify-data
Estrutura de Camadas de Dados
Bronze Layer (Raw)

Dados brutos do MinIO

Preservação do formato original

Timestamp de ingestão

Silver Layer (Cleaned)

Dados limpos e padronizados

Relacionamentos básicos

Qualidade validada

Gold Layer (Business)

Métricas de negócio

Agregações otimizadas

Modelos dimensionais

🔧 Como Usar
Comandos Essenciais
Inicialização Completa
bash
# Script de inicialização automática (criar arquivo start_pipeline.sh)
#!/bin/bash
echo "🎵 Iniciando Pipeline Spotify MDS..."

echo "1. Levantando infraestrutura Docker..."
docker-compose up -d

echo "2. Aguardando serviços inicializarem..."
sleep 60

echo "3. Verificando saúde do sistema..."
python check_system.py

echo "4. Iniciando simulador de dados..."
python main.py --continuous --rate 5

echo "✅ Pipeline em execução!"
echo "📊 Metabase: http://localhost:3000"
echo "🔄 Airflow:  http://localhost:8080"
Verificação do Sistema
bash
# Verificação completa
python check_system.py

# Verificação específica
python check_system.py --check kafka
python check_system.py --check snowflake
python check_system.py --check minio
Simulador de Dados
bash
# Modo contínuo (recomendado)
python main.py --continuous --rate 10

# Modo com duração específica
python main.py --duration 3600 --rate 5

# Modo debug com logs detalhados
python main.py --continuous --rate 2 --verbose

# Gerar dados para região específica
python main.py --region "southeast" --continuous
Acessando as Interfaces
Metabase (BI Dashboard)
bash
# URL: http://localhost:3000
# Login inicial: admin@example.com / admin

# Configurar conexão com Snowflake:
# - Database type: Snowflake
# - Server: sua-conta.snowflakecomputing.com
# - Database: SPOTIFY_ANALYTICS
# - Schema: GOLD
Apache Airflow (Orquestração)
bash
# URL: http://localhost:8080
# Login: airflow / airflow

# DAGs disponíveis:
# - minio_to_snowflake (carga Bronze)
# - snowflake_transform (Silver/Gold)
# - data_quality_checks (validações)
MinIO (Armazenamento)
bash
# URL: http://localhost:9001
# Login: minioadmin / minioadmin

# Verificar dados brutos
# Navegar até bucket 'spotify-data'
Monitoramento do Pipeline
bash
# Ver logs em tempo real
docker-compose logs -f

# Ver métricas específicas
docker stats

# Ver dados fluindo no Kafka
docker exec -it kafka kafka-console-consumer \
  --topic spotify-plays \
  --bootstrap-server localhost:9092 \
  --from-beginning

# Verificar saúde dos serviços
curl http://localhost:8080/health # Airflow
curl http://localhost:3000/api/health # Metabase
📊 Metodologia
Princípios de Engenharia de Dados Aplicados
1. Medallion Architecture
Implementamos as três camadas clássicas:

Bronze: Dados brutos, imutáveis

Silver: Dados limpos, confiáveis

Gold: Dados de negócio, otimizados

2. Data Contracts

Schema validation no Kafka

Testes de qualidade no DBT

Monitoramento contínuo no Airflow

3. Infrastructure as Code

Docker Compose para orquestração

DBT para transformações declarativas

Configurações versionadas no Git

4. Observability

Logs centralizados

Métricas de performance

Alertas de qualidade

Metodologia de Desenvolvimento
Iteração 1: Foundation

Setup da infraestrutura Docker

Configuração dos serviços básicos

Pipeline de dados simples

Iteração 2: Data Quality

Implementação de testes DBT

Validações de schema

Monitoramento de qualidade

Iteração 3: Business Intelligence

Dashboards no Metabase

Métricas de negócio

Visualizações interativas

Métricas de Sucesso
Técnicas:

✅ Latência end-to-end < 5 minutos

✅ Disponibilidade > 99% dos serviços

✅ Dados consistentes entre camadas

Negócio:

✅ Dashboards atualizados em tempo real

✅ Consultas respondidas em < 10 segundos

✅ Interface intuitiva para usuários finais

🔍 Solução de Problemas
Problemas Comuns
1. Docker Compose Falha ao Iniciar
bash
# Verificar se portas estão livres
netstat -tulpn | grep :3000  # Metabase
netstat -tulpn | grep :8080  # Airflow
netstat -tulpn | grep :9092  # Kafka

# Limpar containers anteriores
docker-compose down
docker system prune -f
2. Erros de Conexão com Snowflake
bash
# Verificar credenciais
python -c "
import snowflake.connector
ctx = snowflake.connector.connect(
    user='SEU_USUARIO',
    password='SUA_SENHA', 
    account='SEU_ACCOUNT'
)
print('✅ Conexão OK')
"

# Testar conexão via DBT
cd spotify_dbt
dbt debug
3. Kafka Não Produz/Consome Dados
bash
# Verificar tópicos
docker exec -it kafka kafka-topics --list --bootstrap-server localhost:9092

# Testar produção manual
docker exec -it kafka kafka-console-producer \
  --topic test-topic \
  --bootstrap-server localhost:9092

# Ver consumidores
docker exec -it kafka kafka-consumer-groups --list --bootstrap-server localhost:9092
4. Dados Não Aparecem no Metabase
bash
# Verificar processamento no Airflow
# 1. Acessar http://localhost:8080
# 2. Verificar DAG 'minio_to_snowflake'
# 3. Checar logs das tasks

# Verificar dados no Snowflake
python check_system.py --check snowflake-data
Scripts de Diagnóstico
bash
# Health check completo
./scripts/health_check.sh

# Verificar espaço em disco
docker system df

# Verificar logs de erro
grep -i "error" pipeline_orchestrator.log

# Teste de performance
python benchmarks/pipeline_benchmark.py
📈 Próximos Passos e Melhorias
Melhorias Planejadas
Adicionar Apache Spark para processamento batch

Implementar CDC para dados mestres

Adicionar machine learning para recomendações

Implementar data lineage completo

Adicionar monitoramento com Prometheus/Grafana

Expansões Possíveis
Múltiplas fontes de dados (YouTube Music, Deezer)

Análise de sentimentos de letras

Recomendações em tempo real

Previsão de trends musicais

🤝 Contribuição
Como Contribuir
Fork o projeto

Crie uma branch para sua feature

Commit suas mudanças

Push para a branch

Abra um Pull Request

Padrões de Desenvolvimento
Siga o estilo de código PEP 8 para Python

Use commits semânticos

Mantenha documentação atualizada

Adicione testes para novas funcionalidades

Ambiente de Desenvolvimento
bash
# Setup do ambiente de dev
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate  # Windows

pip install -r requirements-dev.txt
pre-commit install
📞 Suporte e Contato
Documentação Adicional:

Documentação do Airflow

Documentação do DBT

Documentação do Snowflake

Canais de Ajuda:

📋 Issues do GitHub

💬 Discussions

📧 Email

Autor: Maicon Almeida
LinkedIn: aparecidoaalmeida
GitHub: maiconaalmeida

⭐ Se este projeto foi útil, considere dar uma estrela no repositório!

Última atualização: Novembro de 2025