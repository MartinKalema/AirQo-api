resource "google_compute_instance" "pipeline_k8s_worker_0" {
  boot_disk {
    auto_delete = true
    device_name = "pipeline-k8s-worker-0"

    initialize_params {
      image = "https://www.googleapis.com/compute/beta/projects/ubuntu-os-cloud/global/images/ubuntu-2004-focal-v20220712"
      size  = 100
      type  = "pd-balanced"
    }

    mode   = "READ_WRITE"
    source = "https://www.googleapis.com/compute/v1/projects/airqo-250220/zones/europe-west1-b/disks/pipeline-k8s-worker-0"
  }

  confidential_instance_config {
    enable_confidential_compute = false
  }

  machine_type = "n2-highmem-2"

  metadata = {
    ssh-keys = "noah:ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABgQDCGCRMDn3GciJ6EG+uATxHo+FDpOVq9EOcmExdTtcOOb0utD0ayJk7m8cNY9jc2UHphXDAONweRKbhCbMhswQ31ho4im7Gq+373wUGTfsz1AWriupo52AubAAup1tjYeKQrIZ//4R6mw4yx8J98QRWKp2EZwHvw+9ke/3HwWlLEsfhFhLLdCrSG4Slv84djn0MXi40tlAHz8YKlNB88DrMAHwzfdjWnzqIemTcluwwDH2ts6E5LdCVlNLHoocYZudduKxFhcCBBtXR0DpzgKccXQzEN5fdxySPxrcdi9jjTtjYhVBrA3XYAC3kwqdVDClOQzTfA5TfVSGdgYIO5Zyufa9i95W+M+OlnuoiB1zUdOG5GppdUGXUAt9BNO6UY+s/lHKr1/pg26rppSXzwHnS7fEijIrPTpfxRISSsyxuBWjwEcmX7CV9FLjgrzhMd0tUPLHpuR4StbmYrwqfIZXrCN5nOomQPlx4dyacGU+rAWeu0XF0ZvBpxZiMwnTUhfU= noah@Noahs-MacBook.local\nnoah:ecdsa-sha2-nistp256 AAAAE2VjZHNhLXNoYTItbmlzdHAyNTYAAAAIbmlzdHAyNTYAAABBBKZuHPO35LQ/UvmAY0h362h717/8YilFnw1asRNvxGihfgvbNcZZpqriLzm285WEHmrInzyKGF+M59RuaCIZ/yY= google-ssh {\"userName\":\"noah@airqo.net\",\"expireOn\":\"2022-08-03T07:35:31+0000\"}\nnoah:ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAHpAVKfqFgJN6e3QNtbgSaXvjKbuz9dl9ZISJ9aCrD5WT3dX3p4sGicgVzJYoOyITNm1gfuvCN5Vl6P0fhlK5G/IdcMyg8KUi9P/yDdVFfixZs6x6nsDtNdWcLeCpoKWMHOz4qknnUMwuBfrZJgv3TQlXmbZah7WJ/LM844gGbRSAcsEJdBrrv9Sw8aYpA3CCmmrT9ukUDR/LUm0ptkWwcODPrMdm/h0qXVKMm9+SQxbcRFPrjuefkzmhp16t43sJ/Hv+XEJoHqRxnnDhlhxzNTcNpNyH5p+KCrjXmW+iKJJqYiQ7TIwQotbFTiI15W/kVGHAdfc7nUv/6KtHVN1cGM= google-ssh {\"userName\":\"noah@airqo.net\",\"expireOn\":\"2022-08-03T07:35:47+0000\"}"
  }

  name = "pipeline-k8s-worker-0"

  network_interface {
    access_config {
      nat_ip       = "34.78.167.5"
      network_tier = "PREMIUM"
    }

    network            = "https://www.googleapis.com/compute/v1/projects/airqo-250220/global/networks/pipeline-k8s-cluster"
    network_ip         = "10.132.0.15"
    stack_type         = "IPV4_ONLY"
    subnetwork         = "https://www.googleapis.com/compute/v1/projects/airqo-250220/regions/europe-west1/subnetworks/pipeline-k8s-cluster"
    subnetwork_project = "airqo-250220"
  }

  project = "airqo-250220"

  reservation_affinity {
    type = "ANY_RESERVATION"
  }

  scheduling {
    automatic_restart   = true
    on_host_maintenance = "MIGRATE"
    provisioning_model  = "STANDARD"
  }

  service_account {
    email  = "702081712633-compute@developer.gserviceaccount.com"
    scopes = ["https://www.googleapis.com/auth/devstorage.read_only", "https://www.googleapis.com/auth/logging.write", "https://www.googleapis.com/auth/monitoring.write", "https://www.googleapis.com/auth/service.management.readonly", "https://www.googleapis.com/auth/servicecontrol", "https://www.googleapis.com/auth/trace.append"]
  }

  shielded_instance_config {
    enable_integrity_monitoring = true
    enable_vtpm                 = true
  }

  tags = ["http-server", "https-server"]
  zone = "europe-west1-b"
}
# terraform import google_compute_instance.pipeline_k8s_worker_0 projects/airqo-250220/zones/europe-west1-b/instances/pipeline-k8s-worker-0
