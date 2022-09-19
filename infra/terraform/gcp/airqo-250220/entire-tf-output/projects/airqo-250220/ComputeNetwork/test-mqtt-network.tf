resource "google_compute_network" "test_mqtt_network" {
  auto_create_subnetworks = true
  mtu                     = 1460
  name                    = "test-mqtt-network"
  project                 = "airqo-250220"
  routing_mode            = "GLOBAL"
}
# terraform import google_compute_network.test_mqtt_network projects/airqo-250220/global/networks/test-mqtt-network
