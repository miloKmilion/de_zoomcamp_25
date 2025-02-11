# Terraform

Terraform is an infrastructure as code tool that enables you to safely and predictably provision and manage infrastructure in any cloud. Meaning, it gives conditions or infrastructure where code can lives and grow.

> Infrastructure as code.

## Basics

### Why Terraform?

* Simmplicity in keeping track of infrastructure.
* Easier collaboration, since is an unique file it is easy to maintain and collaborate.
* Reproducibility since is easy to recreate in other environments. Or projects, mainaintaining track of the changes.
* Ensure resources are removed, once things are done, then with a quick command things are removed.

### What Terraform is NOT

* Does not manage and update code infrastructure.
* Does not give you the ability to change immutable resources, GCP changing location wll need to move and destroy.
* Not used to manage resources not defined in your terraform files.

### What is terraform

One thing is allow you to make resources from code files.

>Local Machine:
>
>Terraform is inside the local machine <= *provider* => GCP, AWS

__Providers:__ Code that allows terraform to communicate with resource managers as AWS, GCP and others.

### Key Commands

* Init: Gets the provider needed.
* PLan: What am I about to do
* Apply: Do what is in the tf files.
* Destroy: Remove everything defined in the tf files.

## GCP

We need to set a way to tell our local machine to tell GCP where we are and to create resources. For this we need to set a service account, which is never meant to log in into.

the service account will be used by the software to run programs.

To do that we need to set the IAM profile.

> IAM & Admin -> Service Accounts

When creating the service account details we need to specify the access for example Storage admin or BigQuery admin.

After selecting the roles we need to test the access and permissions. To do that we will set a new access Key. These keys are sensitive information ad should not be shared.

we need to set the infrastructure as follows:

```bash
    Terrademo #Folder with the terraform service. 
        keys folder with json keys in it.
        main.tf with the provider configuration.  
```

URL with the config for the bucket:

```html
https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/storage_bucket.html
```

```tf
terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "6.18.1"
    }
  }
}

provider "google" {
  # Configuration options
  # credentials = "./keys/my-creds.json" This is optional and hardcoded.
  project = "fiery-journal-449517-u3"
  region  = "europe-west1"
}

resource "google_storage_bucket" "auto-expire" {
  name          = "fiery-journal-449517-u3"
  location      = "EU"
  force_destroy = true

  lifecycle_rule {
    condition {
      age = 3
    }
    action {
      type = "Delete"
    }
  }

  lifecycle_rule {
    condition {
      age = 1
    }
    action {
      type = "AbortIncompleteMultipartUpload"
    }
  }
}
```

When selecting the provider: ```terraform init```

After Adding the configuration for the storage provider: ```terraform plan```

When both are set: ```terraform apply```

After the things are done: ```terraform destroy```

Important to add the terraform gitignore to the git file and avoid extra files.

```gitignore
# Local .terraform directories
**/.terraform/*

# .tfstate files
*.tfstate
*.tfstate.*

# Crash log files
crash.log
crash.*.log

# Exclude all .tfvars files, which are likely to contain sensitive data, such as
# password, private keys, and other secrets. These should not be part of version 
# control as they are data points which are potentially sensitive and subject 
# to change depending on the environment.
*.tfvars
*.tfvars.json

# Ignore override files as they are usually used to override resources locally and so
# are not checked in
override.tf
override.tf.json
*_override.tf
*_override.tf.json

# Ignore transient lock info files created by terraform apply
.terraform.tfstate.lock.info

# Include override files you do wish to add to version control using negated pattern
# !example_override.tf

# Include tfplan files to ignore the plan output of command: terraform plan -out=tfplan
# example: *tfplan*

# Ignore CLI configuration files
.terraformrc
terraform.rc
```

## Terraform big_query

```terraform
resource "google_bigquery_dataset" "dataset" {
  dataset_id                  = "example_dataset"
  friendly_name               = "test"
  description                 = "This is a test description"
  location                    = "EU"
  default_table_expiration_ms = 3600000

  labels = {
    env = "default"
  }

  access {
    role          = "OWNER"
    user_by_email = google_service_account.bqowner.email
  }

  access {
    role   = "READER"
    domain = "hashicorp.com"
  }
}

resource "google_service_account" "bqowner" {
  account_id = "bqowner"
}
```

## Creating the variables.tf file

Using the variables inside the main.tf file can be not the best option, hence creating the variables.tf file can be used to declare variables.

```terraform
variable "bq_dataset_name" {
  description = "My big query dataset Name"
  default     = "demo_dataset"
}

variable "gcs_storage_class" {
  description = "The GCS storage class for the bucket"
  default     = "STANDARD"
}
```

To be used in the main.tf as ```var.bq_dataset_name```

Paths can be also set as variables as a path and called in the main using the format: ```file('var_credentials')```
