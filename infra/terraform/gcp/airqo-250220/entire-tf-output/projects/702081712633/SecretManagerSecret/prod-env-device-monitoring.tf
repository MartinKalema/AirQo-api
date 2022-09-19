resource "google_secret_manager_secret" "prod_env_device_monitoring" {
  project = "702081712633"

  replication {
    automatic = true
  }

  rotation {
    next_rotation_time = "2022-09-27T21:00:00Z"
    rotation_period    = "2592000s"
  }

  secret_id = "prod-env-device-monitoring"

  topics {
    name = "projects/airqo-250220/topics/secrets-manager"
  }
}
# terraform import google_secret_manager_secret.prod_env_device_monitoring projects/702081712633/secrets/prod-env-device-monitoring
