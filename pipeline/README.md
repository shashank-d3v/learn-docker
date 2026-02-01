# NYC Taxi Data Pipeline

A Python-based data ingestion pipeline that downloads and processes NYC yellow taxi trip data into a PostgreSQL database.

## Overview

This pipeline downloads NYC taxi trip data from the official TLC data repository and ingests it into a PostgreSQL database using chunked processing for memory efficiency.

## Features

- Downloads data from GitHub releases (compressed CSV format)
- Processes data in configurable chunks to manage memory usage
- Creates database schema automatically
- Progress tracking with tqdm
- Configurable database connection parameters

## Dependencies

- pandas: Data manipulation and CSV processing
- SQLAlchemy: Database ORM and connection management
- psycopg2-binary: PostgreSQL driver
- tqdm: Progress bars
- click: Command-line interface

## Installation

```bash
cd pipeline
uv install
```

## Usage

Run the ingestion script with default parameters:

```bash
uv run python ingest_data.py
```

Customize parameters via command line:

```bash
uv run python ingest_data.py \
  --pg-host localhost \
  --pg-port 5432 \
  --pg-db ny_taxi \
  --pg-user root \
  --pg-password root \
  --year 2021 \
  --month 1 \
  --target-table yellow_taxi_data \
  --chunk-size 100000
```

### Command Line Options

- `--pg-host`: PostgreSQL host (default: localhost)
- `--pg-port`: PostgreSQL port (default: 5432)
- `--pg-db`: Database name (default: ny_taxi)
- `--pg-user`: Database user (default: root)
- `--pg-password`: Database password (default: root)
- `--year`: Data year (default: 2021)
- `--month`: Data month (default: 1)
- `--target-table`: Target table name (default: yellow_taxi_data)
- `--chunk-size`: Processing chunk size (default: 100000)

## Data Source

Data is sourced from: https://github.com/DataTalksClub/nyc-tlc-data/releases/download/yellow/

## Database Schema

The pipeline creates a table with the following key columns:
- VendorID, passenger_count, trip_distance
- RatecodeID, store_and_fwd_flag
- PULocationID, DOLocationID (pickup/dropoff locations)
- payment_type, fare_amount, extra, mta_tax
- tip_amount, tolls_amount, improvement_surcharge
- total_amount, congestion_surcharge
- tpep_pickup_datetime, tpep_dropoff_datetime

## Development

To run in development mode with Jupyter notebook support:

```bash
uv run --group dev jupyter notebook
```

Connect to database:

```bash
uv run --group dev pgcli -h localhost -p 5432 -u root -d ny_taxi
```