resource "google_compute_subnetwork" "datalab_network" {
  ip_cidr_range              = "10.146.0.0/20"
  name                       = "datalab-network"
  network                    = "https://www.googleapis.com/compute/v1/projects/airqo-250220/global/networks/datalab-network"
  private_ipv6_google_access = "DISABLE_GOOGLE_ACCESS"
  project                    = "airqo-250220"
  purpose                    = "PRIVATE"
  region                     = "asia-northeast1"
  stack_type                 = "IPV4_ONLY"
}
# terraform import google_compute_subnetwork.datalab_network projects/airqo-250220/regions/asia-northeast1/subnetworks/datalab-network
