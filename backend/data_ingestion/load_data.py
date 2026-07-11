import pandas as pd

from sqlalchemy import text
from sqlalchemy.types import (
    BIGINT,
    BOOLEAN,
    DATE,
    DateTime,
    FLOAT,
    NVARCHAR,
)

from backend.data_ingestion.config import FILES_TO_LOAD
from backend.data_ingestion.db import get_conn
from backend.data_ingestion.utils import read_csv


def infer_sqlalchemy_types(df):
    """
    Infer SQLAlchemy types from pandas DataFrame.
    """

    dtype_map = {}

    for col, dtype in df.dtypes.items():

        if pd.api.types.is_integer_dtype(dtype):
            dtype_map[col] = BIGINT()

        elif pd.api.types.is_float_dtype(dtype):
            dtype_map[col] = FLOAT()

        elif pd.api.types.is_bool_dtype(dtype):
            dtype_map[col] = BOOLEAN()

        elif pd.api.types.is_datetime64_any_dtype(dtype):
            dtype_map[col] = DateTime()

        else:
            try:
                converted = pd.to_datetime(df[col], errors="raise")
                df[col] = converted
                dtype_map[col] = DATE()

            except Exception:
                dtype_map[col] = NVARCHAR(length=500)

    return dtype_map


def load_table(engine, table_name):

    print("=" * 60)
    print(f"Loading table: {table_name}")
    print("=" * 60)

    df = read_csv(table_name)

    print(f"Rows: {len(df)}")

    dtype_map = infer_sqlalchemy_types(df)

    try:
        df.to_sql(
            table_name,
            con=engine,
            if_exists="replace",
            index=False,
            dtype=dtype_map,
            chunksize=500,
        )

        print(f"{table_name} loaded successfully.")

    except Exception as e:
        print(f"Failed loading {table_name}")
        raise e


def validate(engine):

    print("\nValidation Report")
    print("-" * 40)

    with engine.connect() as conn:

        for table in FILES_TO_LOAD:

            try:

                count = conn.execute(
                    text(f"SELECT COUNT(*) FROM {table}")
                ).scalar()

                print(f"{table:<20} {count}")

            except Exception:

                print(f"{table:<20} Not Loaded")


def main():

    engine = get_conn()

    print("=" * 60)
    print("Starting Synthea ETL")
    print("=" * 60)

    for table in FILES_TO_LOAD:

        load_table(engine, table)

    validate(engine)

    print("\nETL Completed Successfully.")


if __name__ == "__main__":
    main()