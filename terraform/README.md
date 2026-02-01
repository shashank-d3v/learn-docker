# Terraform Infrastructure

This directory contains Terraform configuration for provisioning Google Cloud Platform (GCP) infrastructure to support the learn-docker project.

## Overview

The Terraform configuration sets up a Google Cloud Storage (GCS) bucket for storing data and artifacts related to the data pipeline and Docker learning exercises.

## Infrastructure Components

### Google Cloud Storage Bucket
- **Purpose**: Storage for NYC taxi data, pipeline artifacts, and learning materials
- **Naming**: `{project}-learning-bucket-{random_suffix}`
- **Location**: Configurable (default: ASIA)
- **Features**:
  - Uniform bucket-level access enabled
  - Automatic cleanup of incomplete multipart uploads after 1 day
  - Force destroy enabled for easy cleanup

## Prerequisites

1. **Google Cloud Project**: You need a GCP project with billing enabled
2. **Service Account**: A service account with appropriate permissions for Terraform operations
3. **Terraform**: Version 1.0+ installed locally
4. **Google Cloud SDK**: For authentication (optional, can use service account key)

## Authentication

This configuration uses service account impersonation for authentication. The service account email is configured in the Terraform code.

### Required Permissions
The service account needs these IAM roles:
- `roles/storage.admin` - For GCS bucket management
- `roles/iam.serviceAccountTokenCreator` - For service account impersonation

## Configuration

### Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `project` | GCP project ID | - |
| `region` | GCP region | - |
| `zone` | GCP zone | - |
| `location` | GCS bucket location | "ASIA" |

### Variable Files

- `terraform.tfvars`: Contains your specific project values
- Update this file with your GCP project details before running Terraform

## Usage

### Initialize Terraform
```bash
terraform init
```

### Plan Infrastructure Changes
```bash
terraform plan
```

### Apply Infrastructure Changes
```bash
terraform apply
```

### Destroy Infrastructure
```bash
terraform destroy
```

## State Management

- **State File**: `terraform.tfstate` (tracked in git for demo purposes)
- **Lock File**: `.terraform.lock.hcl` (locks provider versions)
- **Backup**: `terraform.tfstate.backup`

> **Note**: In production environments, never commit state files to version control. Use remote state storage like Terraform Cloud or GCS.

## Integration with Data Pipeline

The GCS bucket created by this configuration can be used by the data pipeline in `../pipeline/` for:
- Storing raw NYC taxi data files
- Archiving processed data
- Storing pipeline configuration and logs

## Cost Considerations

- **GCS Storage**: Pay for data storage and operations
- **GCS Lifecycle**: Automatic cleanup helps minimize costs
- **GCP Free Tier**: May cover small learning workloads

## Troubleshooting

### Common Issues

1. **Authentication Errors**
   - Verify service account permissions
   - Check project ID and region settings

2. **Bucket Name Conflicts**
   - Random suffix ensures uniqueness
   - Can be overridden if needed

3. **Provider Version Conflicts**
   - Run `terraform init -upgrade` to update providers

### Useful Commands

```bash
# Validate configuration
terraform validate

# Format code
terraform fmt

# Show current state
terraform show

# List resources
terraform state list
```