# Spotify MDS Pipeline

## Metodologia e guia

Objetivo: mostrar, passo a passo e sem exigir que saiba programar, como levantar o projeto, ver dados passando pela pipeline e checar resultados nas interfaces (Airflow, MinIO, Metabase).

Metodologia (visão conceitual, 6 passos simples)
1. Simular eventos: um "produtor" gera registros de reprodução (main.py).
2. Enviar para fila/streaming: esses registros vão para o Kafka (mensageria).
3. Guardar os dados brutos: um sink salva arquivos no MinIO (S3 compatível) — camada Bronze.
4. Orquestrar e mover: Airflow executa tarefas que lêem os arquivos e carregam para o armazém (Snowflake).
5. Transformar: dbt aplica transformações (Silver → Gold) para criar tabelas prontas para análise.
6. Visualizar: Metabase conecta ao armazém e mostra dashboards com métricas.

O que você verá (sem programar)
- No MinIO: arquivos JSON/Parquet com os eventos gerados.
- No Kafka: tópicos recebendo mensagens (pode checar via logs ou console dentro do container).
- No Airflow: um DAG (spotify_pipeline) que executa etapas da pipeline.
- No Snowflake: schemas e tabelas criadas (se usar Snowflake); se não tiver Snowflake, parte das etapas ficará parcial.
- No Metabase: dashboards prontos com contagens/aggregações.

Passo a passo prático (sem saber programar)

Antes: instale Docker + docker-compose e Git. Se não tiver Snowflake, ainda assim você pode subir tudo localmente — só não terá o armazém remoto funcionando.

1) Clonar e copiar variáveis
- Abra terminal/PowerShell.
- git clone https://github.com/your/repo.git
- cd repo
- Windows: copy .env.sample .env
- Linux/Mac: cp .env.sample .env
    - Dica: não precisa editar .env para testar a maior parte localmente; só se for usar Snowflake ajuste SNOWFLAKE_*.

2) Subir infraestrutura (um comando)
- docker-compose up -d --build
    - O Docker baixa imagens e inicia serviços (Kafka, MinIO, Airflow, Metabase). Aguarde ~1–2 minutos.
    - Se falhar, rode docker-compose logs -f <serviço> para ver erro.

3) Verificar UIs (abra no navegador)
- Airflow: http://localhost:8080 — login: airflow / airflow
    - Ative o DAG "spotify_pipeline" e clique em "Trigger" para executar manualmente.
- MinIO Console: http://localhost:9001 — usuário: minioadmin / minioadmin
    - Abra o bucket (spotify-raw ou nome do .env) e veja arquivos chegando.
- Metabase: http://localhost:3000 — configure senha inicial via UI e veja dashboards prontos.

4) Iniciar o produtor (gera eventos)
- No terminal: python src/main.py --topic spotify.streams --rate 10
    - O script envia eventos para Kafka; cada evento também será salvo em MinIO dependendo da configuração.
    - Se não souber rodar Python: pode pular este passo e apenas forçar o DAG no Airflow para testar ingestão/transformação (algumas DAGs podem depender do produtor).

5) Checar resultados
- MinIO: arquivos novos aparecem no bucket raw/bronze.
- Airflow: monitorar execuções do DAG; abra logs de cada tarefa para ver progresso.
- Metabase: após dbt rodar e dados estarem em Gold, abra dashboards para ver métricas (plays por hora, top tracks, etc).

Comandos rápidos úteis (copiar/colar)
- docker-compose up -d --build
- docker-compose logs -f kafka
- python src/main.py --topic spotify.streams --rate 10
- docker exec -it <airflow_container> bash   (se precisar inspecionar dentro do container)
- dbt (opcional, para transformar): cd dbt && dbt deps && dbt seed && dbt run --profiles-dir ../dbt --target dev

Dicas práticas (visão direta)
- Passo inicial: clone o repositório, copie .env.sample → .env e rode docker-compose up -d --build.
- Para ver o fluxo sem editar código: abra as UIs (Airflow, MinIO, Metabase) e acompanhe os logs; a maior parte funciona por configuração.
- Teste rápido:
    - Suba infra: docker-compose up -d --build
    - Opcional: gerar eventos localmente: python src/main.py --topic spotify.streams --rate 10
    - Ative/execute o DAG spotify_pipeline no Airflow para forçar ingestão/transformação.
- Principais UIs/URLs:
    - Airflow: http://localhost:8080 (airflow/airflow)
    - MinIO Console: http://localhost:9001 (minioadmin/minioadmin)
    - Metabase: http://localhost:3000
- Onde olhar quando algo falha:
    - Logs dos containers: docker-compose logs -f <serviço>
    - Airflow: logs do scheduler/webserver/task instances
    - MinIO: console e permissões do bucket
    - Kafka: logs do broker e tópicos (use kafka-console-consumer dentro do container)
- Correções rápidas comuns:
    - Reiniciar e limpar volumes: docker-compose down -v && docker-compose up -d --build
    - DAGs do Airflow não aparecem: verifique montagem da pasta de dags e permissões; reinicie scheduler/webserver
    - Erros de conexão com Snowflake: confirme SNOWFLAKE_* no .env e teste com SnowSQL/python
- Comandos úteis resumidos:
    - docker-compose up -d --build
    - docker-compose logs -f kafka
    - python src/main.py --topic spotify.streams --rate 10
    - docker exec -it <airflow_container> bash
    - dbt: cd dbt && dbt deps && dbt seed && dbt run --profiles-dir ../dbt --target dev
- Para pedir ajuda: copie o trecho do log com erro e inclua o comando que executou — isso acelera o diagnóstico.

Observação final: foque em abrir as UIs e checar logs primeiro — a maioria dos problemas é evidenciada ali.
- Não precisa editar código para ver o fluxo: execute docker-compose e use as UIs.
- Logs e consoles mostram mensagens claras — se uma etapa falhar, leia o log e pesquise a mensagem.
- Peça ajuda copiando o erro exato; isso facilita diagnóstico.

Problemas comuns e correções rápidas
- Serviço não sobe: docker-compose down -v && docker-compose up -d --build
- Airflow sem DAGs: verifique se a pasta dags está montada e permissões (container logs).
- Sem acesso MinIO: verifique credenciais em .env (MINIO_ROOT_USER/PASSWORD).

Resumo final (um parágrafo)
Este projeto simula todo o fluxo de dados: um produtor gera eventos, Kafka transporta, MinIO guarda o raw, Airflow orquestra movimentações, dbt transforma e Metabase mostra resultados. Para começar sem saber programar, basta clonar, copiar o .env, subir com docker-compose, abrir as UIs (Airflow, MinIO, Metabase) e, opcionalmente, executar python src/main.py para ver os eventos sendo produzidos — a interface e os logs guiarão o restante do processo.

[![Build Status](https://img.shields.io/badge/build-passing-brightgreen)](https://github.com/your/repo/actions)
[![Docker](https://img.shields.io/badge/docker-available-blue?logo=docker)](https://www.docker.com/)
[![Apache Airflow](https://img.shields.io/badge/Airflow-v2.x-orange?logo=apache-airflow)]
[![Kafka](https://img.shields.io/badge/Kafka-available-red?logo=apachekafka)]
[![Snowflake](https://img.shields.io/badge/Snowflake-ready-9cf?logo=snowflake)]
[![DBT](https://img.shields.io/badge/dbt-ready-ff69b4?logo=dbt)]
[![MinIO](https://img.shields.io/badge/MinIO-ready-ffcc00?logo=minio)]
[![Metabase](https://img.shields.io/badge/Metabase-ready-0052cc?logo=metabase)]
[![License: MIT](https://img.shields.io/badge/license-MIT-green)](./LICENSE)

## 📖 Tabela de Conteúdos
- [✨ Funcionalidades](#✨-funcionalidades)
- [🏗️ Arquitetura](#🏗️-arquitetura-do-sistema)
- [🚀 Quick Start (3 minutos)](#🚀-quick-start-3-minutos)
- [⚙️ Instalação Detalhada](#⚙️-instalação-detalhada)
- [🔧 Configuração](#🔧-configuração-detalhada)
- [🎯 Como Usar](#🎯-como-usar)
- [🐛 Troubleshooting](#🐛-troubleshooting)
- [❓ FAQ](#❓-faq)
- [🛠️ Estrutura do Projeto](#🛠️-estrutura-do-projeto)
- [📊 Tabelas e Compatibilidade](#📊-tabelas-e-compatibilidade)
- [🗺️ Roadmap](#🗺️-roadmap-e-melhorias-futuras)
- [🤝 Contribuindo](#🤝-contribuindo)

---

✨ Funcionalidades
- Simulação de dados de streaming do Spotify (produtor: src/main.py)
- Ingestão em tempo real com Apache Kafka
- Armazenamento de objetos com MinIO (S3 compatível)
- Orquestração com Apache Airflow (DAGs para ingestão/transform)
- Armazenamento analítico em Snowflake
- Transformações com dbt (Medallion Architecture: Bronze → Silver → Gold)
- Visualização com Metabase (dashboards prontos)
- Containerização com Docker / docker-compose
- Scripts de verificação e health checks

---

🏗️ Arquitetura do Sistema
Fluxo de dados (ASCII + emojis)
main.py (produtor) 🔁 → Kafka 🟨 → MinIO 🗄️ → Airflow ⚙️ → Snowflake ❄️ → dbt 🛠️ → Metabase 📈

Diagrama simples:
```
[ main.py ]  -->  [ Kafka ]  -->  [ MinIO (raw/bronze) ]
                                   |
                                   v
                                [ Airflow ] --> [ Snowflake (silver/gold) ] -- dbt -->
                                                                        |
                                                                        v
                                                                     [Metabase]
```

Explicação dos componentes:
- main.py: produtor de eventos que simula plays, usuários, dispositivos, timestamps.
- Kafka: tópico(s) de streaming (e.g., spotify.streams) → consumidores simples/Connect.
- MinIO: armazena objetos raw (JSON/Parquet) — camada Bronze.
- Airflow: orquestra consumo, landing → copy para Snowflake, execução dbt.
- Snowflake: armazém analítico; tabelas por camada (bronze/silver/gold).
- dbt: transforma e documenta modelos; executa tests.
- Metabase: conexão direta ao Snowflake para dashboards.

Padrão: Medallion Architecture (Bronze → Silver → Gold)
- Bronze: dados raw sem transformação (MinIO / Snowflake stage)
- Silver: limpeza, deduplicação, enriquecimento
- Gold: agregações e tabelas prontas para BI

---

🚀 Quick Start (3 minutos)
Pré-requisitos: Docker, docker-compose, Git, python >=3.8, Snowflake account (ou usar Snowflake trial).

Comandos EXATOS:

Windows (PowerShell):
```powershell
git clone https://github.com/your/repo.git
cd repo
copy .env.sample .env
docker-compose up -d --build
# aguardar serviços subirem (~30-90s)
docker-compose logs -f kafka   # verificar kafka
# iniciar produtor local (opcional)
python src/main.py
# rodar DAGs/DBT via Airflow webserver/scheduler (veja URLs abaixo)
```

Linux / Mac (bash):
```bash
git clone https://github.com/your/repo.git
cd repo
cp .env.sample .env
docker-compose up -d --build
# verificar serviços
docker-compose logs -f kafka
# opcional: iniciar produtor
python src/main.py
```

Comandos para executar testes:
```bash
pytest --cov=src tests/unit
```

URLs e credenciais padrão (variáveis em .env; exemplo):
- Airflow UI: http://localhost:8080 (user: airflow / pass: airflow)
- MinIO Console: http://localhost:9001 (user: minioadmin / pass: minioadmin)
- Kafka (broker): localhost:9092
- Metabase: http://localhost:3000 (setup inicial via UI)
- Snowflake: usar credenciais em .env (SNOWFLAKE_ACCOUNT, USER, PASSWORD, ROLE, WAREHOUSE, DATABASE, SCHEMA)

Observação: ajuste credenciais em .env antes de executar.

---

⚙️ Instalação Detalhada

1. Clonar repositório
2. Copiar variáveis de exemplo
   - Linux/Mac: cp .env.sample .env
   - Windows: copy .env.sample .env
3. Editar .env com credenciais do Snowflake e opções do MinIO
4. Levantar infra com Docker Compose:
   - docker-compose up -d --build
5. Executar health checks:
   - Linux/Mac: ./scripts/check_env.sh
   - Python: python scripts/health_check.py

Instruções específicas por SO:
- Windows: use PowerShell com permissão de administrador; assegure WSL2 se usar Docker Desktop.
- Linux: garanta permissões de rede e ulimits para Kafka.
- Mac: habilite recursos do Docker Desktop (CPU/RAM adequados).

Arquivo .env (variáveis obrigatórias)
- MINIO_ROOT_USER=
- MINIO_ROOT_PASSWORD=
- MINIO_BUCKET=
- KAFKA_BROKER=localhost:9092
- SNOWFLAKE_ACCOUNT=
- SNOWFLAKE_USER=
- SNOWFLAKE_PASSWORD=
- SNOWFLAKE_ROLE=
- SNOWFLAKE_WAREHOUSE=
- SNOWFLAKE_DATABASE=
- SNOWFLAKE_SCHEMA=
- DBT_PROFILES_DIR=./dbt
- AIRFLOW__CORE__FERNET_KEY=...
- AIRFLOW__CORE__LOAD_EXAMPLES=False

Configuração de conexões Airflow (exemplos via Airflow UI/Admin -> Connections)
- kafka_conn (kafka://localhost:9092)
- minio_s3 (s3://minioadmin:minioadmin@minio:9000)
- snowflake_default (using Snowflake hook; account, user, password)

Snowflake — passos rápidos
1. Conectar via SnowSQL ou UI.
2. Criar warehouse/database/schema:
```sql
CREATE WAREHOUSE IF NOT EXISTS MDS_WH WITH WAREHOUSE_SIZE = 'XSMALL' WAREHOUSE_TYPE = 'STANDARD' AUTO_SUSPEND = 60;
CREATE DATABASE IF NOT EXISTS SPOTIFY_MDS;
USE DATABASE SPOTIFY_MDS;
CREATE SCHEMA IF NOT EXISTS RAW;
CREATE SCHEMA IF NOT EXISTS SILVER;
CREATE SCHEMA IF NOT EXISTS GOLD;
```
3. Criar role/user e conceder privilégios (exemplo minimal):
```sql
CREATE ROLE IF NOT EXISTS mds_role;
GRANT USAGE ON WAREHOUSE MDS_WH TO ROLE mds_role;
GRANT USAGE ON DATABASE SPOTIFY_MDS TO ROLE mds_role;
GRANT ALL ON SCHEMA SPOTIFY_MDS.RAW TO ROLE mds_role;
GRANT ALL ON SCHEMA SPOTIFY_MDS.SILVER TO ROLE mds_role;
GRANT ALL ON SCHEMA SPOTIFY_MDS.GOLD TO ROLE mds_role;
```
4. Preencha variáveis SNOWFLAKE_* no .env.

---

🎯 Como Usar
Executar produtor:
```bash
python src/main.py --topic spotify.streams --rate 10
```
Verificar tópicos Kafka:
```bash
docker exec -it kafka-container kafka-topics --bootstrap-server localhost:9092 --list
docker exec -it kafka-container kafka-console-consumer --bootstrap-server localhost:9092 --topic spotify.streams --from-beginning --max-messages 5
```
Airflow:
- Acesse http://localhost:8080
- Ative o DAG spotify_pipeline
- Forçar execução para testes

dbt:
```bash
cd dbt
dbt deps
dbt seed
dbt run --profiles-dir ../dbt --target dev
dbt test
```

Exemplo de registro gerado (JSON):
```json
{
  "user_id":"u_123",
  "track_id":"t_456",
  "played_at":"2025-11-06T12:34:56Z",
  "device":"mobile",
  "duration_ms":210000
}
```

---

🐛 Troubleshooting (erros comuns)

1. Kafka não sobe / broker não disponível
   - Comando: docker-compose logs -f kafka
   - Solução: aumentar ulimits, remover volumes e reiniciar: docker-compose down -v && docker-compose up -d

2. Airflow DAGs não aparecem
   - Verifique AIRFLOW__CORE__DAGS_FOLDER, permissões e reinicie scheduler/webserver
   - Logs: docker-compose logs -f airflow-scheduler

3. Conexão Snowflake falha
   - Teste com SnowSQL ou python:
```python
from snowflake.connector import connect
conn = connect(user='USER', password='PW', account='ACCT')
```
   - Confira SNOWFLAKE_ACCOUNT e ROLE

4. MinIO acesso negado
   - Console: http://localhost:9001
   - Credenciais default: minioadmin:minioadmin (alterar em .env)

Comandos úteis para diagnóstico:
- docker ps
- docker-compose logs -f <service>
- kafka-topics, kafka-console-consumer (dentro do container)
- dbt debug --profiles-dir dbt

Logs a checar:
- Airflow: scheduler, webserver, worker
- Kafka: broker, zookeeper
- MinIO: server
- Snowflake: ver query history no UI

---

❓ FAQ
Q: Posso usar Snowflake trial?
A: Sim. Preencha SNOWFLAKE_ACCOUNT e credenciais no .env.

Q: Quanto tempo demora para subir tudo?
A: ~30s–2min dependendo da máquina; Kafka/MinIO/DB inicialização podem levar mais.

Q: Preciso de Internet para rodar?
A: Sim, para baixar imagens Docker na primeira vez e para Snowflake se estiver usando conta remota.

Q: Posso substituir MinIO por S3 real?
A: Sim — configure endpoint e credenciais S3 no .env e ajuste conexões.

---

📊 Tabelas e Compatibilidade

Tabela de compatibilidade de SO
| Sistema | Docker | Testado | Observações |
|---|---:|---:|---|
| Windows 10/11 (WSL2 recomendado) | ✅ | ✅ | Use PowerShell/WSL2 |
| Ubuntu 20.04+ | ✅ | ✅ | Ajuste ulimits para Kafka |
| macOS (Intel/Apple Silicon) | ✅ | ✅ | Docker Desktop recomendado |

Tabela de componentes principais
| Componente | Função | Local |
|---|---|---|
| Kafka | Ingestão streaming | container kafka |
| MinIO | Armazenamento objetos (Bronze) | container minio |
| Airflow | Orquestração | container airflow |
| Snowflake | Armazenamento analítico | cloud |
| dbt | Transformações (Silver/Gold) | dbt/ |
| Metabase | Visualizações | container metabase |
| Producer (main.py) | Simula eventos | src/main.py |

---

🗺️ Roadmap e melhorias futuras
- Autenticação centralizada e secrets manager (Vault)
- Kafka Connect para CDC e sinks adicionais
- Deploy Kubernetes (Helm charts)
- CI/CD para dbt models e tests (GitHub Actions)
- Monitoramento (Prometheus + Grafana)
- Suporte a particionamento e compactação no S3/MinIO

---

📸 Sugestões de capturas de tela (placeholders)
- <!-- SCREENSHOT: Airflow UI mostrando DAG ativo — capture http://localhost:8080 with DAG spotify_pipeline expanded -->
- <!-- SCREENSHOT: MinIO Console mostrando bucket spotify-raw -->
- <!-- SCREENSHOT: Metabase dashboard com métricas de plays por hora -->
- <!-- SCREENSHOT: dbt docs site / lineage gráfico -->

---

🛠️ Estrutura do Projeto
- src/: produtor e micro-serviços de ingestão
- config/: arquivos de configuração
- db/: scripts SQL e migrations
- dbt/: modelos dbt, seeds e profiles
- dags/: DAGs do Airflow
- tests/: testes unitários e de integração
- scripts/: health checks, helpers
- docker/: Dockerfiles e overrides
- .github/workflows/: CI/CD

---

✅ Validação e health checks incluídos
- scripts/check_env.sh (bash)
- scripts/health_check.py (python)
- dbt tests para modelos críticos
- DAGs Airflow com sensors e retries

---

🤝 Contribuindo
- Leia CONTRIBUTING.md
- Use branches feature/* e PRs
- Escreva testes para mudanças e atualize docs/dbt docs

---

Licença
MIT — veja LICENSE para detalhes.


Este projeto simula um ambiente de produção real. Pipeline completo de dados em tempo real, pronto para uso com configuração mínima — ideal para aprendizado de Modern Data Stack.

## Como rodar
1. Copiar .env.sample para .env
2. Rodar `docker-compose up -d`
3. Executar `python src/main.py`
4. Rodar testes com `pytest --cov=src tests/unit`
