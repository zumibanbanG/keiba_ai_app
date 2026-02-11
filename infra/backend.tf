terraform {
  required_version = "1.14.4"

  required_providers {
    google = {
        source = "hashicorp/google"
        version = "7.19.0"
    }
  }

  backend "gcs" {
    bucket = "keiba-ai-terraform-bucket"
    prefix = "tfstate"
  }
}

provider "google" {
  project = local.project_id
  region  = local.region
}