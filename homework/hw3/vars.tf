variable "project" {
  type        = string
  description = "GCP project ID"
}

variable "region" {
  type        = string
  description = "GCP region"
}

variable "zone" {
  type        = string
  description = "GCP zone"
}

variable "location" {
  type        = string
  description = "GCS bucket location (e.g., ASIA or asia-south1)"
  default     = "ASIA"
}

variable "target_service_account" {
  type        = string
  description = "The service account to impersonate for GCP operations"
}

variable "bq_location" {
  type    = string
  default = "asia-south1"
}
