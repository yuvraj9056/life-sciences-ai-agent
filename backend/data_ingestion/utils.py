from pathlib import Path
import pandas as pd

BASE_PATH = Path("datasets/structured/synthea/required_files")


def read_csv(table_name: str):

    df = pd.read_csv(BASE_PATH / f"{table_name}.csv")

    # Remove leading/trailing spaces from column names
    df.columns = [c.strip() for c in df.columns]

    return df