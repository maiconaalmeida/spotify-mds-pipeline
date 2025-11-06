# Spotify MDS Pipeline

Pipeline de dados para extrair, transformar e carregar informações da API do Spotify.

## Estrutura do Projeto
- src/: Código ETL modularizado
- config/: Configurações e variáveis de ambiente
- db/: Banco de dados e migrations
- models/: Modelos analíticos/dbt
- tests/: Testes unitários e de integração
- scripts/: Utilitários
- docker/: Dockerfiles
- .github/workflows/: CI/CD

## Como rodar
1. Copiar .env.sample para .env
2. Rodar `docker-compose up -d`
3. Executar `python src/main.py`
4. Rodar testes com `pytest --cov=src tests/unit`