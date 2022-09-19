resource "google_compute_disk" "airqo_k8s_pd_storage" {
  description               = "Persistent disk storage to be consumed by k8s"
  name                      = "airqo-k8s-pd-storage"
  physical_block_size_bytes = 4096
  project                   = "airqo-250220"
  size                      = 50
  type                      = "pd-standard"
  zone                      = "europe-west1-b"
}
# terraform import google_compute_disk.airqo_k8s_pd_storage projects/airqo-250220/zones/europe-west1-b/disks/airqo-k8s-pd-storage
