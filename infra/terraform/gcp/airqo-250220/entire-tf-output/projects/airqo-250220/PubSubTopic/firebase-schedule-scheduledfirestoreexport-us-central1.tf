resource "google_pubsub_topic" "firebase_schedule_scheduledfirestoreexport_us_central1" {
  name    = "firebase-schedule-scheduledFirestoreExport-us-central1"
  project = "airqo-250220"
}
# terraform import google_pubsub_topic.firebase_schedule_scheduledfirestoreexport_us_central1 projects/airqo-250220/topics/firebase-schedule-scheduledFirestoreExport-us-central1
