resource "google_artifact_registry_repository" "this" {
    location = local.region
    project = local.project_id
    repository_id = "keiba-ai-repo"
    format = "DOCKER"
    description = "Artifact Registry for Web Application Docker Images"

    lifecycle {
      prevent_destroy = true
    }
}


resource "google_cloud_run_v2_service" "web_app" {
  project = local.project_id
  name     = "keiba-ai"
  location = local.region
  deletion_protection = false

  template {
    containers {
      image = "us-central1-docker.pkg.dev/keiba-ai-487108/keiba-ai-repo/web:latest"

      env {
        name  = "ENVIRONMENT"
        value = ""
      }

      resources {
        limits = {
          memory = "1024Mi"
          cpu    = "2"
        }
      }

      ports {
        container_port = 8501
      }
    }
  }
}

resource "google_cloud_run_v2_service_iam_binding" "allow_public_invoker" {
  project = google_cloud_run_v2_service.web_app.project
  location = google_cloud_run_v2_service.web_app.location
  name = google_cloud_run_v2_service.web_app.name
  role    = "roles/run.invoker"
  members = [
    "allUsers",
  ]
}

resource "google_cloud_run_v2_job" "batch_job" {
  project = local.project_id
  name     = "keiba-collector"
  location = local.region
  deletion_protection = false

  template {
    template {
      max_retries = 1
      timeout = "10800s"
      containers {
        image = "us-central1-docker.pkg.dev/keiba-ai-487108/keiba-ai-repo/batch:latest"

        env {
          name  = "YEAR"
          value = "2023"
        }
        env {
          name  = "PLACE_ID"
          value = "05"
        }

        resources {
          limits = {
            memory = "512Mi"
            cpu    = "1"
          }
        }
      }
    }
  }
}