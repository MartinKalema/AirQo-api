resource "google_pubsub_topic" "calculate_exceedances_for_last_28_days" {
  name    = "calculate_exceedances_for_last_28_days"
  project = "airqo-250220"
}
# terraform import google_pubsub_topic.calculate_exceedances_for_last_28_days projects/airqo-250220/topics/calculate_exceedances_for_last_28_days
