docker run --rm --network=homework_default taxi_ingest:v002 \
  scripts_ingest/ingest_green_parquet.py \
  --user root --password root --host pgdatabase --port 5432 --db ny_taxi \
  --table_name green_tripdata_2025_11 \
  --file extraction/data/green_tripdata_2025-11.parquet


  docker run --rm --network=homework_default taxi_ingest:v002 \
  scripts_ingest/ingest_zone_lookup.py \
  --user root --password root --host pgdatabase --port 5432 --db ny_taxi \
  --table_name taxi_zone_lookup \
  --file extraction/data/taxi_zone_lookup.csv