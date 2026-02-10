# HW3: GCS and BigQuery (External + Native Tables)

This folder contains my completed setup for Homework 3:
1. Upload Yellow Taxi Parquet files (Jan to Jun 2024) to Google Cloud Storage.
2. Create BigQuery dataset and tables:
   - External table over the Parquet files in GCS
   - Native BigQuery table created from the external table (no partitioning or clustering)
3. Create an additional partitioned + clustered table for comparison.

## GCP Project Details

- Project: `<project-id>`
- Dataset: `<dataset-name>`
- Bucket (Terraform output): `gs://<your-bucket-name>`
- Service Account (impersonated): `<impersonated-service-account-email>`

## Approach Used

- No service account key files were created.
- Authentication is via ADC (Application Default Credentials) using `gcloud auth application-default login`.
- Terraform uses service account impersonation via `impersonate_service_account`.
- Python script also uses service account impersonation (no JSON key) and uses Terraform outputs for `BUCKET_NAME`, `GCP_PROJECT`, and `TARGET_SERVICE_ACCOUNT`.

## Prerequisites

- `gcloud` installed and authenticated
- `terraform` installed
- `uv` installed (to run the Python script)
- Required APIs enabled:
  - `iam.googleapis.com`
  - `iamcredentials.googleapis.com`
  - `cloudresourcemanager.googleapis.com`
  - `storage.googleapis.com`

## One Time IAM Setup (Impersonation)

Create Service Account and grant permissions:

- Grant the caller (my user) permission to impersonate the service account:
  - `roles/iam.serviceAccountTokenCreator`
  - `roles/iam.serviceAccountUser`

- Grant the service account permissions for GCS bucket creation and object uploads:
  - `roles/storage.admin`

Note: The impersonation worked only after granting both:
- `roles/iam.serviceAccountTokenCreator`
- `roles/iam.serviceAccountUser`

## Terraform

### What Terraform provisions
- GCS bucket with a random suffix
- BigQuery dataset: `hw3` (location: `asia-south1`)
- BigQuery external table: `yellow_tripdata_2024_external`
- BigQuery native table: `yellow_tripdata_2024` created using a BigQuery query job

### Run Terraform
From the `hw3/` folder (repo root level for this homework):

```bash
terraform init -upgrade
terraform apply
````

### Export outputs for Python

```bash
export BUCKET_NAME="$(terraform output -raw bucket_name)"
export TARGET_SERVICE_ACCOUNT="$(terraform output -raw target_service_account)"
export GCP_PROJECT="$(terraform output -raw project_id)"
```

## Python (Upload Parquet Files to GCS)

Script path:

* `homework/hw3/load_yellow_taxi_data.py`

Run from the repo root:

```bash
uv run python homework/hw3/load_yellow_taxi_data.py
```

Expected:

* Downloads `yellow_tripdata_2024-01.parquet` to `yellow_tripdata_2024-06.parquet`
* Uploads all files to `gs://$BUCKET_NAME/`
* Verifies each upload

## BigQuery Objects Created

* External table:

  * `de-2026-hws.hw3.yellow_tripdata_2024_external`

* Native table:

  * `de-2026-hws.hw3.yellow_tripdata_2024`

* Partitioned + clustered table (created via SQL):

  * `de-2026-hws.hw3.yellow_tripdata_2024_part_clust`
  * Partition: `DATE(tpep_dropoff_datetime)`
  * Cluster: `VendorID`

## SQL Snippets (Homework Queries)

```sql
-- External table
SELECT count(*) FROM `de-2026-hws.hw3.yellow_tripdata_2024_external` LIMIT 1000;

-- Materialized Table(NATIVE Table)
SELECT COUNT(1) FROM `de-2026-hws.hw3.yellow_tripdata_2024`;

-- Distinct PULocationID count on the NATIVE table
SELECT COUNT(DISTINCT PULocationID) AS distinct_pulocationids
FROM `de-2026-hws.hw3.yellow_tripdata_2024`;

-- Distinct PULocationID count on the EXTERNAL table
SELECT COUNT(DISTINCT PULocationID) AS distinct_pulocationids
FROM `de-2026-hws.hw3.yellow_tripdata_2024_external`;

-- Retrieve PULocationID from the native table
SELECT PULocationID
FROM `de-2026-hws.hw3.yellow_tripdata_2024`;

-- Retrieve PULocationID and DOLocationID from the same native table
SELECT
  PULocationID,
  DOLocationID
FROM `de-2026-hws.hw3.yellow_tripdata_2024`;

-- Records having fare_amount as 0
SELECT COUNT(1) AS zero_fare_records -- COUNT(1) as we are counting rows, not a column
FROM `de-2026-hws.hw3.yellow_tripdata_2024`
WHERE fare_amount = 0;

-- Creating partioned table with cluser on the NATIVE Table
CREATE OR REPLACE TABLE `de-2026-hws.hw3.yellow_tripdata_2024_part_clust`
PARTITION BY DATE(tpep_dropoff_datetime)
CLUSTER BY VendorID AS
SELECT *
FROM `de-2026-hws.hw3.yellow_tripdata_2024`;

-- Query to retrieve the distinct VendorIDs 
-- between tpep_dropoff_datetime 2024-03-01 and 2024-03-15 
-- (inclusive) from NATIVE Table
SELECT DISTINCT VendorID
FROM `de-2026-hws.hw3.yellow_tripdata_2024`
WHERE tpep_dropoff_datetime >= TIMESTAMP('2024-03-01')
  AND tpep_dropoff_datetime <  TIMESTAMP('2024-03-16')
ORDER BY VendorID;

-- Query to retrieve the distinct VendorIDs 
-- between tpep_dropoff_datetime 2024-03-01 and 2024-03-15 
-- (inclusive) from Partioned NATIVE Table 
SELECT DISTINCT VendorID
FROM `de-2026-hws.hw3.yellow_tripdata_2024_part_clust`
WHERE tpep_dropoff_datetime >= TIMESTAMP('2024-03-01')
  AND tpep_dropoff_datetime <  TIMESTAMP('2024-03-16')
ORDER BY VendorID;
```

## Notes

* External table reads Parquet directly from GCS.
* Native table stores data inside BigQuery storage (no partitioning/clustering as required).
* BigQuery `COUNT(*)` on the native table may show `0 B processed` because BigQuery can answer using metadata/statistics without scanning the underlying data.