#!/usr/bin/env bash
set -euo pipefail

mkdir -p data

GREEN_URL="https://d37ci6vzurychx.cloudfront.net/trip-data/green_tripdata_2025-11.parquet"
ZONES_URL="https://github.com/DataTalksClub/nyc-tlc-data/releases/download/misc/taxi_zone_lookup.csv"

echo "Downloading green trip parquet..."
wget -q --show-progress -O "data/green_tripdata_2025-11.parquet" "$GREEN_URL"

echo "Downloading taxi zone lookup csv..."
wget -q --show-progress -O "data/taxi_zone_lookup.csv" "$ZONES_URL"

echo "Done. Files in ./data"
ls -lh data
