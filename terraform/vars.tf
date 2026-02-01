variable "project" {
  type        = string
  description = "GCP project ID"
}

variable "project_name" {
  type        = string
  description = "GCP project name"
}

variable "region" {
  type        = string
  description = "GCP region"
}

variable "zone" {
  type        = string
  description = "GCP zone"
}

# variable "bucket_name" {
#   type        = string
#   description = "Globally unique GCS bucket name"
# }

variable "location" {
  type        = string
  description = "GCS bucket location (e.g., ASIA or asia-south1)"
  default     = "ASIA"
}

variable "target_service_account" {
  type        = string
  description = "The service account to impersonate for GCP operations"
}

variable "gcs_storage_class" {
  description = "Bucket Storage Class"
  default     = "STANDARD"
}

# variable "gcs_bucket_name" {
#   description = "Bucket Storage Name"
#   default = "STANDARD"
# }

variable "bq_dataset" {
  description = "BigQuery Dataset"
  default     = "demo_dataset"
}
