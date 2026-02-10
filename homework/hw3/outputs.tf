output "bucket_name" {
  value = google_storage_bucket.hw3_bucket.name
}

output "target_service_account" {
  value = var.target_service_account
}

output "project_id" {
  value = var.project
}

output "bq_dataset" {
  value = google_bigquery_dataset.hw3.dataset_id
}

output "bq_external_table" {
  value = google_bigquery_table.yellow_2024_external.table_id
}

output "bq_native_table" {
  value = "yellow_tripdata_2024"
}
