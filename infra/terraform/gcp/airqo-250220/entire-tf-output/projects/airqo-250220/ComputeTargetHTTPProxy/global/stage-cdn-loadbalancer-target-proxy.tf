resource "google_compute_target_http_proxy" "stage_cdn_loadbalancer_target_proxy" {
  name    = "stage-cdn-loadbalancer-target-proxy"
  project = "airqo-250220"
  url_map = "https://www.googleapis.com/compute/v1/projects/airqo-250220/global/urlMaps/stage-cdn-loadbalancer"
}
# terraform import google_compute_target_http_proxy.stage_cdn_loadbalancer_target_proxy projects/airqo-250220/global/targetHttpProxies/stage-cdn-loadbalancer-target-proxy
