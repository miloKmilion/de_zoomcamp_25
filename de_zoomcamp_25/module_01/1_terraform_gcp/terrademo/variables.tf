variable "bq_dataset_name" {
  description = "My big query dataset Name"
  default     = "demo_dataset"
}

variable "gcs_storage_class" {
  description = "The GCS storage class for the bucket"
  default     = "STANDARD"
}

variable "gcs_bucket_name" {
  description = "The GCS bucket storage name"
  default     = "fiery-journal-449517-u3"
}

variable "location" {
  description = "Project location"
  default     = "EU"
}

variable "region" {
  description = "Project region"
  default     = "europe-west1"
}

variable "credentials" {
  description = "My Google account credentials"
  default = "./keys/my-creds.json"
}