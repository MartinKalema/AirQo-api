resource "google_service_account" "mikebq3" {
  account_id   = "mikebq3"
  description  = "creating Big Query jobs"
  display_name = "MikeBQ3"
  project      = "airqo-250220"
}
# terraform import google_service_account.mikebq3 projects/airqo-250220/serviceAccounts/mikebq3@airqo-250220.iam.gserviceaccount.com
