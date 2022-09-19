resource "google_compute_route" "kubernetes_5fd4397d_5ca3_4071_8a81_0b7bc8cc83ab" {
  description       = "k8s-node-route"
  dest_range        = "10.244.1.0/24"
  name              = "kubernetes-5fd4397d-5ca3-4071-8a81-0b7bc8cc83ab"
  network           = "https://www.googleapis.com/compute/v1/projects/airqo-250220/global/networks/pipeline-k8s-cluster"
  next_hop_instance = "projects/airqo-250220/zones/us-central1-a/instances/pipeline-k8s-worker-0"
  priority          = 1000
  project           = "airqo-250220"
}
# terraform import google_compute_route.kubernetes_5fd4397d_5ca3_4071_8a81_0b7bc8cc83ab projects/airqo-250220/global/routes/kubernetes-5fd4397d-5ca3-4071-8a81-0b7bc8cc83ab
