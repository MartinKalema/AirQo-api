resource "google_compute_subnetwork" "datalab_network" {
  ip_cidr_range = "10.206.0.0/20"
  name          = "datalab-network"
  network       = "https://www.googleapis.com/compute/v1/projects/airqo-250220/global/networks/datalab-network"
  project       = "airqo-250220"
  purpose       = "PRIVATE"
  region        = "us-south1"
  stack_type    = "IPV4_ONLY"
}
# terraform import google_compute_subnetwork.datalab_network projects/airqo-250220/regions/us-south1/subnetworks/datalab-network
