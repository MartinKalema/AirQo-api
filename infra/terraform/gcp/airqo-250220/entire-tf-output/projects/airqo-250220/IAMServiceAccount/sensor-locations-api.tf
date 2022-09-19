resource "google_service_account" "sensor_locations_api" {
  account_id   = "sensor-locations-api"
  display_name = "sensor-locations-api"
  project      = "airqo-250220"
}
# terraform import google_service_account.sensor_locations_api projects/airqo-250220/serviceAccounts/sensor-locations-api@airqo-250220.iam.gserviceaccount.com
