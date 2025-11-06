from src.extract import fetch_spotify_data
from src.transform import clean_data
from src.load import write_to_db
from config.config import get_config
import logging

logging.basicConfig(level=logging.INFO)

def main():
    config = get_config()
    logging.info("Iniciando pipeline...")
    
    data = fetch_spotify_data(config["spotify"])
    df_clean = clean_data(data)
    write_to_db(df_clean, config["database"])
    
    logging.info("Pipeline finalizado com sucesso!")

if __name__ == "__main__":
    main()