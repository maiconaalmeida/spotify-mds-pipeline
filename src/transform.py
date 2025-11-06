import pandas as pd

def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    df = df.drop_duplicates()
    df = df.fillna({'popularity': 0, 'release_date': '1970-01-01'})
    return df