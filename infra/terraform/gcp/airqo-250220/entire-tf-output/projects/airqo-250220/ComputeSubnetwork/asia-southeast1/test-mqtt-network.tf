resource "google_compute_subnetwork" "test_mqtt_network" {
  ip_cidr_range              = "10.148.0.0/20"
  name                       = "test-mqtt-network"
  network                    = "https://www.googleapis.com/compute/v1/projects/airqo-250220/global/networks/test-mqtt-network"
  private_ipv6_google_access = "DISABLE_GOOGLE_ACCESS"
  project                    = "airqo-250220"
  purpose                    = "PRIVATE"
  region                     = "asia-southeast1"
  stack_type                 = "IPV4_ONLY"
}
# terraform import google_compute_subnetwork.test_mqtt_network projects/airqo-250220/regions/asia-southeast1/subnetworks/test-mqtt-network
