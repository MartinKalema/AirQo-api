resource "google_secret_manager_secret" "sta_env_netmanager" {
  project = "702081712633"

  replication {
    automatic = true
  }

  secret_id = "sta-env-netmanager"

  topics {
    name = "projects/airqo-250220/topics/secrets-manager"
  }
}
# terraform import google_secret_manager_secret.sta_env_netmanager projects/702081712633/secrets/sta-env-netmanager
