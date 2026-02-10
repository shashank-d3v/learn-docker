resource "google_bigquery_dataset" "hw3" {
  dataset_id                 = "hw3"
  location                   = var.bq_location
  description                = "HW3 dataset for Yellow Taxi 2024 Jan-Jun"
  delete_contents_on_destroy = true
}

# External table over Parquet files in GCS
resource "google_bigquery_table" "yellow_2024_external" {
  dataset_id = google_bigquery_dataset.hw3.dataset_id
  table_id   = "yellow_tripdata_2024_external"

  external_data_configuration {
    source_format = "PARQUET"
    autodetect    = true

    source_uris = [
      "gs://${google_storage_bucket.hw3_bucket.name}/yellow_tripdata_2024-*.parquet"
    ]
  }
  deletion_protection = false
}

resource "random_id" "bq_job_suffix" {
  byte_length = 4
}

# Regular (native) table created via a query job from the external table
resource "google_bigquery_job" "yellow_2024_native_create" {
  job_id   = "hw3_yellow_2024_native_${random_id.bq_job_suffix.hex}"
  location = var.bq_location

  query {
    use_legacy_sql = false
    query          = <<SQL
SELECT * FROM `${var.project}.hw3.yellow_tripdata_2024_external`;
SQL

    destination_table {
      project_id = var.project
      dataset_id = google_bigquery_dataset.hw3.dataset_id
      table_id   = "yellow_tripdata_2024"
    }

    create_disposition = "CREATE_IF_NEEDED"
    write_disposition  = "WRITE_TRUNCATE"
  }

  depends_on = [google_bigquery_table.yellow_2024_external]
}
