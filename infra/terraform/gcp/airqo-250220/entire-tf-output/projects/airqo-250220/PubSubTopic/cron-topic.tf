resource "google_pubsub_topic" "cron_topic" {
  name    = "cron-topic"
  project = "airqo-250220"
}
# terraform import google_pubsub_topic.cron_topic projects/airqo-250220/topics/cron-topic
