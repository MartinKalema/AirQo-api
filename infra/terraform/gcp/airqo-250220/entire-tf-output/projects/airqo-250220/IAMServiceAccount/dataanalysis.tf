resource "google_service_account" "dataanalysis" {
  account_id   = "dataanalysis"
  display_name = "dataAnalysis"
  project      = "airqo-250220"
}
# terraform import google_service_account.dataanalysis projects/airqo-250220/serviceAccounts/dataanalysis@airqo-250220.iam.gserviceaccount.com
