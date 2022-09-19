resource "google_compute_subnetwork" "datalab_network" {
  ip_cidr_range              = "10.152.0.0/20"
  name                       = "datalab-network"
  network                    = "https://www.googleapis.com/compute/v1/projects/airqo-250220/global/networks/datalab-network"
  private_ipv6_google_access = "DISABLE_GOOGLE_ACCESS"
  project                    = "airqo-250220"
  purpose                    = "PRIVATE"
  region                     = "australia-southeast1"
  stack_type                 = "IPV4_ONLY"
}
# terraform import google_compute_subnetwork.datalab_network projects/airqo-250220/regions/australia-southeast1/subnetworks/datalab-network
