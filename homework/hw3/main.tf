terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "7.16.0"
    }
    random = {
      source  = "hashicorp/random"
      version = "3.6.3"
    }
  }
}

provider "google" {
  project = var.project
  region  = var.region
  zone    = var.zone

  # This makes ALL Google resources use SA impersonation
  impersonate_service_account = var.target_service_account
}

resource "random_id" "bucket_suffix" {
  byte_length = 4
}

resource "google_storage_bucket" "hw3_bucket" {
  name                        = "${var.project}-hw3-bucket-${random_id.bucket_suffix.hex}"
  location                    = var.location
  force_destroy               = true
  uniform_bucket_level_access = true

  lifecycle_rule {
    condition { age = 1 }
    action { type = "AbortIncompleteMultipartUpload" }
  }
}
