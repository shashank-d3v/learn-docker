import os
import sys
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor

import google.auth
from google.auth import impersonated_credentials
from google.cloud import storage

# ----------------------------
# Required environment vars
# ----------------------------
# Export these from Terraform outputs before running:
#   export BUCKET_NAME="$(terraform output -raw bucket_name)"
#   export TARGET_SERVICE_ACCOUNT="$(terraform output -raw target_service_account)"
#   export GCP_PROJECT="$(terraform output -raw project_id)"
PROJECT_ID = os.environ["GCP_PROJECT"]
BUCKET_NAME = os.environ["BUCKET_NAME"]
TARGET_SERVICE_ACCOUNT = os.environ["TARGET_SERVICE_ACCOUNT"]

# ----------------------------
# Download settings
# ----------------------------
BASE_URL = "https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2024-"
MONTHS = [f"{i:02d}" for i in range(1, 7)]
DOWNLOAD_DIR = "."
CHUNK_SIZE = 8 * 1024 * 1024
MAX_WORKERS = int(os.environ.get("MAX_WORKERS", "4"))
MAX_RETRIES = int(os.environ.get("MAX_RETRIES", "3"))
RETRY_SLEEP_SECONDS = int(os.environ.get("RETRY_SLEEP_SECONDS", "5"))

os.makedirs(DOWNLOAD_DIR, exist_ok=True)


def make_impersonated_storage_client() -> storage.Client:
    """
    Creates a Google Cloud Storage client using Service Account impersonation.
    Requires:
      - gcloud auth application-default login completed
      - caller has roles/iam.serviceAccountTokenCreator and roles/iam.serviceAccountUser on TARGET_SERVICE_ACCOUNT
    """
    source_creds, _ = google.auth.default(
        scopes=["https://www.googleapis.com/auth/cloud-platform"]
    )

    target_creds = impersonated_credentials.Credentials(
        source_credentials=source_creds,
        target_principal=TARGET_SERVICE_ACCOUNT,
        target_scopes=["https://www.googleapis.com/auth/cloud-platform"],
        lifetime=3600,
    )

    return storage.Client(project=PROJECT_ID, credentials=target_creds)


def download_file(month: str) -> str | None:
    url = f"{BASE_URL}{month}.parquet"
    file_path = os.path.join(DOWNLOAD_DIR, f"yellow_tripdata_2024-{month}.parquet")

    try:
        print(f"Downloading {url}...")
        urllib.request.urlretrieve(url, file_path)
        print(f"Downloaded: {file_path}")
        return file_path
    except Exception as e:
        print(f"Failed to download {url}: {e}")
        return None


def verify_gcs_upload(client: storage.Client, bucket: storage.Bucket, blob_name: str) -> bool:
    return storage.Blob(bucket=bucket, name=blob_name).exists(client)


def upload_to_gcs(
    client: storage.Client,
    bucket: storage.Bucket,
    file_path: str,
    max_retries: int = MAX_RETRIES,
) -> None:
    blob_name = os.path.basename(file_path)
    blob = bucket.blob(blob_name)
    blob.chunk_size = CHUNK_SIZE

    for attempt in range(max_retries):
        try:
            print(
                f"Uploading {file_path} to gs://{bucket.name}/ (Attempt {attempt + 1}/{max_retries})..."
            )
            blob.upload_from_filename(file_path)
            print(f"Uploaded: gs://{bucket.name}/{blob_name}")

            if verify_gcs_upload(client, bucket, blob_name):
                print(f"Verification successful for {blob_name}")
                return

            print(f"Verification failed for {blob_name}, retrying...")
        except Exception as e:
            print(f"Failed to upload {file_path}: {e}")

        time.sleep(RETRY_SLEEP_SECONDS)

    print(f"Giving up on {file_path} after {max_retries} attempts.")


def main() -> int:
    client = make_impersonated_storage_client()

    # Terraform already created the bucket. Do not create it here.
    bucket = client.bucket(BUCKET_NAME)

    # Optional: quick existence check (fails fast if BUCKET_NAME is wrong)
    try:
        client.get_bucket(BUCKET_NAME)
        print(f"Using existing bucket: gs://{BUCKET_NAME}/")
    except Exception as e:
        print(f"Bucket not accessible or does not exist: gs://{BUCKET_NAME}/")
        print(f"Details: {e}")
        return 1

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        file_paths = list(executor.map(download_file, MONTHS))

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = []
        for fp in filter(None, file_paths):
            futures.append(executor.submit(upload_to_gcs, client, bucket, fp))

        # Ensure exceptions surface
        for f in futures:
            f.result()

    print("All files processed and verified.")
    print(f"Bucket used: gs://{bucket.name}/")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
