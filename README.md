# 🎧 Projeto Spotify Modern Data Stack

Este projeto apresenta uma pipeline de Engenharia de Dados completa e em tempo real para análise de música do Spotify, utilizando as principais tecnologias da Modern Data Stack (MDS).

![Snowflake](https://img.shields.io/badge/Snowflake-29B5E8?logo=snowflake&logoColor=white)
![DBT](https://img.shields.io/badge/dbt-FF694B?logo=dbt&logoColor=white)
![Apache Airflow](https://img.shields.io/badge/Apache%20Airflow-017CEE?logo=apacheairflow&logoColor=white)
![Apache Kafka](https://img.shields.io/badge/Apache%20Kafka-231F20?logo=apachekafka&logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB?logo=python&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2496ED?logo=docker&logoColor=white)
![Power BI](https://img.shields.io/badge/Power%20BI-F2C811?logo=powerbi&logoColor=black)
![Modern Data Stack](https://img.shields.io/badge/Modern%20Data%20Stack-00C7B7?logo=databricks&logoColor=white)

---

## 📌 Visão Geral do Projeto

O objetivo é simular dados de streaming de música do Spotify — incluindo **reproduções de músicas, ouvintes, regiões e tipos de dispositivos** — e construir uma **pipeline totalmente automatizada** que vai da ingestão em tempo real até a visualização de insights de negócios.

Uma vez iniciada, a pipeline é **autônoma**: simulação de dados → streaming via Kafka → armazenamento no Snowflake → transformação com DBT → visualização no Power BI.

### ✅ Funcionalidades Principais

* **Pipeline em Tempo Real:** Ingestão contínua de dados de streaming usando **Apache Kafka**.
* **Arquitetura Medallion:** Implementação das camadas **Bronze → Silver → Gold** no Snowflake para garantir qualidade e governança.
* **Transformação Modular:** Utilização do **DBT** para modelagem de dados limpa, testável e documentada.
* **Orquestração:** Gerenciamento de todo o fluxo de trabalho (ingestão e transformação) via **Apache Airflow**.
* **Visualização:** Dashboard interativo no **Power BI** para insights de tendências de música e ouvintes.
* **Contêinerização:** Ambiente totalmente configurado e replicável usando **Docker e `docker-compose`**.

---

## 🏗️ Arquitetura da Solução

A pipeline segue um fluxo lógico e moderno para processamento de dados em tempo real.

<img width="5600" height="2898" alt="Arquitetura" src="https://github.com/user-attachments/assets/290a5f78-6992-4e19-8fcf-a1c973e75885" />

### Detalhamento do Fluxo

1.  **Simulador de Dados (Python/Faker):** Gera dados falsos de streaming de música (evento de reprodução) em um loop contínuo.
2.  **Kafka Producer:** Envia cada evento de reprodução de música para tópicos Kafka em tempo real.
3.  **Kafka Consumer:** Consome as mensagens do Kafka e as armazena como arquivos **JSON brutos** no **MinIO** (que atua como um Data Lake compatível com S3).
4.  **Apache Airflow (Orquestração):**
    * **DAG 1:** Agenda e executa o carregamento dos arquivos brutos do MinIO para a **Camada Bronze** do Snowflake.
    * **DAG 2:** Aciona as transformações do DBT para construir as camadas Silver e Gold.
5.  **Snowflake (Data Warehouse):** Armazena os dados nas três camadas (Bronze, Silver, Gold).
6.  **DBT (Transformação):** Executa modelos SQL complexos para limpar, padronizar e agregar dados, criando as tabelas finais de análise.
7.  **Power BI (BI):** Conecta-se diretamente à **Camada Gold** do Snowflake para visualizações interativas.

---

## ⚡ Stack Tecnológico

| Componente | Ferramenta | Função na Pipeline |
| :--- | :--- | :--- |
| **Simulação** | Python (Faker) | Geração de dados de streaming. |
| **Streaming** | Apache Kafka | Transporte de dados em tempo real. |
| **Data Lake** | MinIO | Armazenamento de objetos (S3-compatible) para dados brutos. |
| **Data Warehouse** | Snowflake | Armazenamento e gerenciamento de dados na nuvem. |
| **Transformação** | DBT (data build tool) | Modelagem analítica (SQL) e testes. |
| **Orquestração** | Apache Airflow | Agendamento e monitoramento de workflows. |
| **Visualização** | Power BI | Geração de dashboards e insights. |
| **Ambiente** | Docker/Docker Compose | Conteinerização e gerenciamento de serviços. |

---

## ⚙️ Detalhes da Implementação

### 1. Modelagem no Snowflake (Arquitetura Medallion)

* **Bronze:** Contém os dados brutos, tal como vieram do Kafka/MinIO. O esquema de dados é preservado (`raw_data`).
* **Silver:** Dados limpos, padronizados, deduplicados e enriquecidos. Prontos para serem modelados (Staging/Intermediate).
* **Gold:** Camada de agregação de negócios. Contém as *Data Marts* (fatos e dimensões) otimizadas para consumo de BI.

### 2. Transformações com DBT

O DBT é usado para aplicar as transformações de negócios e garantir a qualidade dos dados:

* **Staging Models:** Limpeza de colunas, tratamento de valores nulos e padronização de tipos de dados.
* **Marts de Negócios:** Construção de **tabelas fato** (`plays`, `listeners`) e **tabelas dimensão** (`tracks`, `artists`, `regions`) na Camada Gold.
* **Qualidade de Dados:** Aplicação de `dbt test` para verificar unicidade, não-nulidade e referências, garantindo a integridade dos dados antes da visualização.

### 3. Dashboard do Power BI

O dashboard interativo oferece as seguintes análises:

<img width="1313" height="728" alt="dashboard (2)" src="https://github.com/user-attachments/assets/87b4b28d-9dfa-4346-8550-0a7f05718455" />

* 🎵 **Métricas Chave:** Total de Reproduções, Ouvintes Únicos.
* 🌎 **Análise Geográfica:** Mapa de calor exibindo reproduções por região (e.g., estados dos EUA).
* 📈 **Tendências:** Reproduções ao longo do tempo (diárias, horárias).
* 💽 **Distribuição:** Gráfico de distribuição por tipo de dispositivo (Mobile, Desktop, Web).

---

## 📂 Estrutura do Repositório

```text
spotify-mds-pipeline/
├── docker/ # Arquivos de configuração do Docker e Airflow DAGs
│   ├── .env
│   ├── docker-compose.yml
│   └── dags/
│       ├── minio-to-kafka.py # DAG para ingestão
│       └── .env
├── spotify_dbt/ # Projeto DBT
│   └── models/
│       ├── gold/ # Tabelas finais de BI
│       ├── silver/ # Modelos intermediários (Staging)
│       └── sources.yml # Definição das fontes de dados (Camada Bronze)
├── simulator/ # Scripts de Simulação
│   ├── producer.py # Gera e envia dados para o Kafka
│   └── .env
├── consumer/ # Script Consumidor
│   ├── kafka-to-minio.py # Consome do Kafka e salva no MinIO
│   └── .env
├── docker-compose.yml # Arquivo principal para subir todos os serviços
├── requirements.txt
└── README.md

Certamente! Aqui está o arquivo README.md completo, formatado e traduzido para o português, baseado nas informações que você forneceu.

Markdown

# 🎧 Projeto Spotify Modern Data Stack

Este projeto apresenta uma pipeline de Engenharia de Dados completa e em tempo real para análise de música do Spotify, utilizando as principais tecnologias da Modern Data Stack (MDS).

![Snowflake](https://img.shields.io/badge/Snowflake-29B5E8?logo=snowflake&logoColor=white)
![DBT](https://img.shields.io/badge/dbt-FF694B?logo=dbt&logoColor=white)
![Apache Airflow](https://img.shields.io/badge/Apache%20Airflow-017CEE?logo=apacheairflow&logoColor=white)
![Apache Kafka](https://img.shields.io/badge/Apache%20Kafka-231F20?logo=apachekafka&logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB?logo=python&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2496ED?logo=docker&logoColor=white)
![Power BI](https://img.shields.io/badge/Power%20BI-F2C811?logo=powerbi&logoColor=black)
![Modern Data Stack](https://img.shields.io/badge/Modern%20Data%20Stack-00C7B7?logo=databricks&logoColor=white)

---

## 📌 Visão Geral do Projeto

O objetivo é simular dados de streaming de música do Spotify — incluindo **reproduções de músicas, ouvintes, regiões e tipos de dispositivos** — e construir uma **pipeline totalmente automatizada** que vai da ingestão em tempo real até a visualização de insights de negócios.

Uma vez iniciada, a pipeline é **autônoma**: simulação de dados → streaming via Kafka → armazenamento no Snowflake → transformação com DBT → visualização no Power BI.

### ✅ Funcionalidades Principais

* **Pipeline em Tempo Real:** Ingestão contínua de dados de streaming usando **Apache Kafka**.
* **Arquitetura Medallion:** Implementação das camadas **Bronze → Silver → Gold** no Snowflake para garantir qualidade e governança.
* **Transformação Modular:** Utilização do **DBT** para modelagem de dados limpa, testável e documentada.
* **Orquestração:** Gerenciamento de todo o fluxo de trabalho (ingestão e transformação) via **Apache Airflow**.
* **Visualização:** Dashboard interativo no **Power BI** para insights de tendências de música e ouvintes.
* **Contêinerização:** Ambiente totalmente configurado e replicável usando **Docker e `docker-compose`**.

---

## 🏗️ Arquitetura da Solução

A pipeline segue um fluxo lógico e moderno para processamento de dados em tempo real.

<img width="5600" height="2898" alt="Arquitetura" src="https://github.com/user-attachments/assets/290a5f78-6992-4e19-8fcf-a1c973e75885" />

### Detalhamento do Fluxo

1.  **Simulador de Dados (Python/Faker):** Gera dados falsos de streaming de música (evento de reprodução) em um loop contínuo.
2.  **Kafka Producer:** Envia cada evento de reprodução de música para tópicos Kafka em tempo real.
3.  **Kafka Consumer:** Consome as mensagens do Kafka e as armazena como arquivos **JSON brutos** no **MinIO** (que atua como um Data Lake compatível com S3).
4.  **Apache Airflow (Orquestração):**
    * **DAG 1:** Agenda e executa o carregamento dos arquivos brutos do MinIO para a **Camada Bronze** do Snowflake.
    * **DAG 2:** Aciona as transformações do DBT para construir as camadas Silver e Gold.
5.  **Snowflake (Data Warehouse):** Armazena os dados nas três camadas (Bronze, Silver, Gold).
6.  **DBT (Transformação):** Executa modelos SQL complexos para limpar, padronizar e agregar dados, criando as tabelas finais de análise.
7.  **Power BI (BI):** Conecta-se diretamente à **Camada Gold** do Snowflake para visualizações interativas.

---

## ⚡ Stack Tecnológico

| Componente | Ferramenta | Função na Pipeline |
| :--- | :--- | :--- |
| **Simulação** | Python (Faker) | Geração de dados de streaming. |
| **Streaming** | Apache Kafka | Transporte de dados em tempo real. |
| **Data Lake** | MinIO | Armazenamento de objetos (S3-compatible) para dados brutos. |
| **Data Warehouse** | Snowflake | Armazenamento e gerenciamento de dados na nuvem. |
| **Transformação** | DBT (data build tool) | Modelagem analítica (SQL) e testes. |
| **Orquestração** | Apache Airflow | Agendamento e monitoramento de workflows. |
| **Visualização** | Power BI | Geração de dashboards e insights. |
| **Ambiente** | Docker/Docker Compose | Conteinerização e gerenciamento de serviços. |

---

## ⚙️ Detalhes da Implementação

### 1. Modelagem no Snowflake (Arquitetura Medallion)

* **Bronze:** Contém os dados brutos, tal como vieram do Kafka/MinIO. O esquema de dados é preservado (`raw_data`).
* **Silver:** Dados limpos, padronizados, deduplicados e enriquecidos. Prontos para serem modelados (Staging/Intermediate).
* **Gold:** Camada de agregação de negócios. Contém as *Data Marts* (fatos e dimensões) otimizadas para consumo de BI.

### 2. Transformações com DBT

O DBT é usado para aplicar as transformações de negócios e garantir a qualidade dos dados:

* **Staging Models:** Limpeza de colunas, tratamento de valores nulos e padronização de tipos de dados.
* **Marts de Negócios:** Construção de **tabelas fato** (`plays`, `listeners`) e **tabelas dimensão** (`tracks`, `artists`, `regions`) na Camada Gold.
* **Qualidade de Dados:** Aplicação de `dbt test` para verificar unicidade, não-nulidade e referências, garantindo a integridade dos dados antes da visualização.

### 3. Dashboard do Power BI

O dashboard interativo oferece as seguintes análises:

<img width="1313" height="728" alt="dashboard (2)" src="https://github.com/user-attachments/assets/87b4b28d-9dfa-4346-8550-0a7f05718455" />

* 🎵 **Métricas Chave:** Total de Reproduções, Ouvintes Únicos.
* 🌎 **Análise Geográfica:** Mapa de calor exibindo reproduções por região (e.g., estados dos EUA).
* 📈 **Tendências:** Reproduções ao longo do tempo (diárias, horárias).
* 💽 **Distribuição:** Gráfico de distribuição por tipo de dispositivo (Mobile, Desktop, Web).

---

## 📂 Estrutura do Repositório

```text
spotify-mds-pipeline/
├── docker/ # Arquivos de configuração do Docker e Airflow DAGs
│   ├── .env
│   ├── docker-compose.yml
│   └── dags/
│       ├── minio-to-kafka.py # DAG para ingestão
│       └── .env
├── spotify_dbt/ # Projeto DBT
│   └── models/
│       ├── gold/ # Tabelas finais de BI
│       ├── silver/ # Modelos intermediários (Staging)
│       └── sources.yml # Definição das fontes de dados (Camada Bronze)
├── simulator/ # Scripts de Simulação
│   ├── producer.py # Gera e envia dados para o Kafka
│   └── .env
├── consumer/ # Script Consumidor
│   ├── kafka-to-minio.py # Consome do Kafka e salva no MinIO
│   └── .env
├── docker-compose.yml # Arquivo principal para subir todos os serviços
├── requirements.txt
└── README.md


🚀 Como Executar o Projeto
(Instruções detalhadas para configuração de credenciais, subida dos contêineres via docker-compose up, e inicialização da simulação e do Airflow seriam incluídas aqui)

Configuração: Preencha o arquivo .env com suas credenciais do Snowflake.

Inicialização: Suba todos os serviços conteinerizados: docker-compose up -d.

Simulação: Execute o script producer.py para iniciar o fluxo de dados em tempo real.

Airflow: Acesse a UI do Airflow e ative/execute as DAGs de ingestão e transformação.

Visualização: Conecte o Power BI à Camada Gold do Snowflake e visualize o dashboard
