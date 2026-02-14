terraform {
  required_version = "1.14.4"

  required_providers {
    google = {
        source = "hashicorp/google"
        version = "7.12.0"
    }
  }

  backend "gcs" {
    bucket = "keiba-ai-terraform-bucket"
    prefix = "tfstate"
  }
}