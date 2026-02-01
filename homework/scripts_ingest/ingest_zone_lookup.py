import argparse
import os
import re
import sys
import time
from typing import Optional

import pandas as pd
from sqlalchemy import create_engine, text


def safe_table_name(name: str) -> str:
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


def main():
    parser = argparse.ArgumentParser(description="Ingest taxi_zone_lookup csv into Postgres")
    parser.add_argument("--user", required=True)
    parser.add_argument("--password", required=True)
    parser.add_argument("--host", required=True)
    parser.add_argument("--port", type=int, default=5432)
    parser.add_argument("--db", required=True)
    parser.add_argument("--table_name", required=True)
    parser.add_argument("--file", required=True, help="Path to CSV file")
    args = parser.parse_args()

    table_name = safe_table_name(args.table_name)

    if not os.path.exists(args.file):
        raise FileNotFoundError(f"File not found: {args.file}")

    engine = create_engine(make_pg_url(args.user, args.password, args.host, args.port, args.db))
    wait_for_postgres(engine)

    df = pd.read_csv(args.file)
    df.columns = [re.sub(r"[^a-zA-Z0-9]+", "_", c).strip("_").lower() for c in df.columns]

    # common schema: locationid, borough, zone, service_zone
    if "locationid" in df.columns:
        df["locationid"] = pd.to_numeric(df["locationid"], errors="coerce")

    df.to_sql(
        name=table_name,
        con=engine,
        if_exists="replace",
        index=False,
        method="multi",
        chunksize=10_000,
    )

    with engine.begin() as conn:
        if "locationid" in df.columns:
            conn.execute(text(f"CREATE INDEX IF NOT EXISTS idx_{table_name}_locationid ON {table_name} (locationid)"))

    print(f"Done. Loaded {len(df)} rows into {table_name}.")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)
