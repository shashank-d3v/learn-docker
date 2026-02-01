#!/usr/bin/env python3
# coding: utf-8

import io
import time
import pandas as pd
from tqdm.auto import tqdm
from sqlalchemy import create_engine
from sqlalchemy.types import BigInteger, String
import click

URL = "https://github.com/DataTalksClub/nyc-tlc-data/releases/download/misc/taxi_zone_lookup.csv"

PANDAS_DTYPE = {
    "LocationID": "Int64",
    "Borough": "string",
    "Zone": "string",
    "service_zone": "string",
}

SQL_TYPES = {
    "LocationID": BigInteger(),
    "Borough": String(),
    "Zone": String(),
    "service_zone": String(),
}

def open_csv_iterator(url: str, chunk_size: int, retries: int = 3, backoff_sec: int = 2):
    last_err = None
    for attempt in range(1, retries + 1):
        try:
            return pd.read_csv(
                url,
                dtype=PANDAS_DTYPE,
                iterator=True,
                chunksize=chunk_size,
            )
        except Exception as e:
            last_err = e
            if attempt < retries:
                time.sleep(backoff_sec * attempt)
            else:
                raise last_err

def copy_insert(conn, full_table_name: str, df: pd.DataFrame):
    """
    Fast Postgres bulk load using COPY FROM STDIN.
    - Uses \\N for NULLs.
    - No header, CSV format, columns in df order.
    """
    buf = io.StringIO()
    df.to_csv(buf, index=False, header=False, na_rep="\\N")
    buf.seek(0)

    cols = ",".join([f'"{c}"' for c in df.columns])
    sql = f"COPY {full_table_name} ({cols}) FROM STDIN WITH (FORMAT CSV, NULL '\\N')"

    raw = conn.connection  # DBAPI connection (psycopg2)
    cur = raw.cursor()
    try:
        cur.copy_expert(sql, buf)
    finally:
        cur.close()

@click.command()
@click.option("--pg-host", default="localhost", show_default=True)
@click.option("--pg-port", type=int, default=5432, show_default=True)
@click.option("--pg-db", default="ny_taxi", show_default=True)
@click.option("--pg-user", default="root", show_default=True)
@click.option("--pg-pass", default="root", show_default=True)
@click.option("--target-table", default="taxi_zone_lookup", show_default=True)
@click.option("--schema", default="public", show_default=True)
@click.option("--chunk-size", type=int, default=10_000, show_default=True)
@click.option(
    "--if-exists",
    type=click.Choice(["replace", "append", "fail"], case_sensitive=False),
    default="replace",
    show_default=True,
)
@click.option(
    "--insert-method",
    type=click.Choice(["copy", "multi", "default"], case_sensitive=False),
    default="copy",
    show_default=True,
)
@click.option(
    "--to-sql-chunksize",
    type=int,
    default=2_000,
    show_default=True,
    help="Used only when insert-method is multi/default",
)
def run(
    pg_host, pg_port, pg_db, pg_user, pg_pass,
    target_table, schema, chunk_size,
    if_exists, insert_method, to_sql_chunksize
):
    table_name = target_table
    full_table = f'{schema}."{table_name}"'

    engine = create_engine(
        f"postgresql://{pg_user}:{pg_pass}@{pg_host}:{pg_port}/{pg_db}",
        pool_pre_ping=True,
    )

    df_iter = open_csv_iterator(URL, chunk_size=chunk_size)

    first = True
    inserted_rows = 0

    with engine.begin() as conn:
        for df_chunk in tqdm(df_iter, desc=f"Loading {table_name}"):
            if first:
                df_chunk.head(0).to_sql(
                    name=table_name,
                    con=conn,
                    schema=schema,
                    if_exists=if_exists,
                    index=False,
                    dtype=SQL_TYPES,
                )
                first = False

            if insert_method == "copy":
                copy_insert(conn, full_table, df_chunk)
            elif insert_method == "multi":
                df_chunk.to_sql(
                    name=table_name,
                    con=conn,
                    schema=schema,
                    if_exists="append",
                    index=False,
                    method="multi",
                    chunksize=to_sql_chunksize,
                    dtype=SQL_TYPES,
                )
            else:  # "default"
                df_chunk.to_sql(
                    name=table_name,
                    con=conn,
                    schema=schema,
                    if_exists="append",
                    index=False,
                    chunksize=to_sql_chunksize,
                    dtype=SQL_TYPES,
                )

            inserted_rows += len(df_chunk)

    print(f"Done. Inserted rows: {inserted_rows}. Table: {schema}.{table_name}. Method: {insert_method}")

if __name__ == "__main__":
    run()
