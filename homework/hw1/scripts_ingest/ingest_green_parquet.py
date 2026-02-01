import argparse
import math
import os
import re
import sys
import time
from typing import Optional

import pandas as pd
from sqlalchemy import create_engine, text


def safe_table_name(name: str) -> str:
    # allow letters, digits, underscore only
    cleaned = re.sub(r"[^a-zA-Z0-9_]+", "_", name).strip("_")
    if not cleaned:
        raise ValueError("Invalid table_name after sanitization.")
    return cleaned.lower()


def make_pg_url(user: str, password: str, host: str, port: int, db: str) -> str:
    return f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{db}"


def wait_for_postgres(engine, timeout_s: int = 60) -> None:
    start = time.time()
    last_err: Optional[Exception] = None
    while time.time() - start < timeout_s:
        try:
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            return
        except Exception as e:
            last_err = e
            time.sleep(2)
    raise RuntimeError(f"Postgres not reachable within {timeout_s}s. Last error: {last_err}")


def normalize_green_columns(df: pd.DataFrame) -> pd.DataFrame:
    # Normalize column names to snake_case and lower
    df.columns = [re.sub(r"[^a-zA-Z0-9]+", "_", c).strip("_").lower() for c in df.columns]

    # Common TLC green schema columns sometimes appear with different casing
    # Ensure datetime columns are parsed when present
    for col in ["lpep_pickup_datetime", "lpep_dropoff_datetime"]:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")

    # Optional: enforce integer-ish columns if present
    int_cols = ["passenger_count", "trip_distance", "payment_type", "ratecodeid", "pulocationid", "dolocationid"]
    for col in int_cols:
        if col in df.columns:
            # keep NaN allowed
            df[col] = pd.to_numeric(df[col], errors="coerce")

    return df


def main():
    parser = argparse.ArgumentParser(description="Ingest green tripdata parquet into Postgres")
    parser.add_argument("--user", required=True)
    parser.add_argument("--password", required=True)
    parser.add_argument("--host", required=True)
    parser.add_argument("--port", type=int, default=5432)
    parser.add_argument("--db", required=True)
    parser.add_argument("--table_name", required=True)
    parser.add_argument("--file", required=True, help="Path to parquet file")
    parser.add_argument("--chunksize", type=int, default=200_000)
    args = parser.parse_args()

    table_name = safe_table_name(args.table_name)

    if not os.path.exists(args.file):
        raise FileNotFoundError(f"File not found: {args.file}")

    engine = create_engine(make_pg_url(args.user, args.password, args.host, args.port, args.db))
    wait_for_postgres(engine)

    # Read parquet (whole file) then push in chunks to Postgres
    df = pd.read_parquet(args.file)
    df = normalize_green_columns(df)

    total_rows = len(df)
    if total_rows == 0:
        print("No rows found in parquet. Exiting.")
        return

    n_chunks = math.ceil(total_rows / args.chunksize)
    print(f"Loaded parquet rows={total_rows}. Writing to table={table_name} in {n_chunks} chunk(s).")

    # Write first chunk with replace to create table, then append
    for i in range(n_chunks):
        start = i * args.chunksize
        end = min((i + 1) * args.chunksize, total_rows)
        chunk = df.iloc[start:end].copy()

        if_exists = "replace" if i == 0 else "append"
        t0 = time.time()
        chunk.to_sql(
            name=table_name,
            con=engine,
            if_exists=if_exists,
            index=False,
            method="multi",
            chunksize=20_000,
        )
        dt = time.time() - t0
        print(f"Chunk {i+1}/{n_chunks} rows {start}:{end} written ({end-start} rows) in {dt:.1f}s")

    # Useful indexes for typical queries
    with engine.begin() as conn:
        if "lpep_pickup_datetime" in df.columns:
            conn.execute(text(f"CREATE INDEX IF NOT EXISTS idx_{table_name}_pickup_dt ON {table_name} (lpep_pickup_datetime)"))
        if "pulocationid" in df.columns:
            conn.execute(text(f"CREATE INDEX IF NOT EXISTS idx_{table_name}_pulocationid ON {table_name} (pulocationid)"))
        if "dolocationid" in df.columns:
            conn.execute(text(f"CREATE INDEX IF NOT EXISTS idx_{table_name}_dolocationid ON {table_name} (dolocationid)"))

    print("Done.")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)
