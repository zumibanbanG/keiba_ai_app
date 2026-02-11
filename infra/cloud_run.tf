resource "google_artifact_registry_repository" "this" {
    location = local.region
    project = local.project_id
    repository_id = "keiba-ai-repo"
    format = "DOCKER"
    description = "Artifact Registry for Web Application Docker Images"
}


resource "google_cloud_run_v2_service" "web_app" {
  project = local.project_id
  name     = "web-application"
  location = local.region
  deletion_protection = false

  template {
    containers {
      image = "gcr.io/my-project/web-application:latest"

      env {
        name  = "ENVIRONMENT"
        value = ""
      }

      resources {
        limits = {
          memory = "256Mi"
          cpu    = "1"
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
  name     = "data-processor-job"
  location = local.region
  deletion_protection = false

  template {
    template {
      max_retries = 3
      timeout = "600s"
      containers {
        image = "gcr.io/my-project/data-processor:latest"

        env {
          name  = "ENVIRONMENT"
          value = ""
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