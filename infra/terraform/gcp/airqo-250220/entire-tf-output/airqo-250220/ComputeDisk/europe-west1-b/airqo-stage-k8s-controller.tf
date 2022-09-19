resource "google_compute_disk" "airqo_stage_k8s_controller" {
  image                     = "https://www.googleapis.com/compute/beta/projects/ubuntu-os-cloud/global/images/ubuntu-1804-bionic-v20210720"
  name                      = "airqo-stage-k8s-controller"
  physical_block_size_bytes = 4096
  project                   = "airqo-250220"
  size                      = 100
  type                      = "pd-standard"
  zone                      = "europe-west1-b"
}
# terraform import google_compute_disk.airqo_stage_k8s_controller projects/airqo-250220/zones/europe-west1-b/disks/airqo-stage-k8s-controller
