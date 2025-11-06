import pandas as pd

def write_to_db(df: pd.DataFrame, db_config):
    # Exemplo: conexão com Postgres (psycopg2)
    print(f"Dados prontos para serem carregados no banco {db_config['DB_NAME']}")