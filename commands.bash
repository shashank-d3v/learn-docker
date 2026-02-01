# Run them all from \pipeline

# Run the Containerized Ingestion
docker run -it   --network=pipeline_default   taxi_ingest:v001     --pg-user=root     --pg-pass=root     --pg-host=pgdatabase     --pg-port=5432     --pg-db=ny_taxi     --target-table=yellow_taxi_trips --month=12 --year=2020

# Run pgAdmin Container 
docker run -it \
  -e PGADMIN_DEFAULT_EMAIL="admin@admin.com" \
  -e PGADMIN_DEFAULT_PASSWORD="root" \
  -v pgadmin_data:/var/lib/pgadmin \
  -p 8085:80 \
  --network=pg-network \
  --name pgadmin \
  dpage/pgadmin4

# Run PostgreSQL Container
docker run -it \
  -e POSTGRES_USER="root" \
  -e POSTGRES_PASSWORD="root" \
  -e POSTGRES_DB="ny_taxi" \
  -v ny_taxi_postgres_data:/var/lib/postgresql \
  -p 5432:5432 \
  --network=pg-network \
  --name pgdatabase \
  postgres:18

