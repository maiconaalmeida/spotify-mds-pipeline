import pandas as pd

def fetch_spotify_data(config):
    # Exemplo de fetch de API
    data = [{"track": "Song1", "artist": "Artist1", "popularity": 50}]
    df = pd.DataFrame(data)
    return df