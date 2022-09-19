resource "google_bigquery_table" "geo_census" {
  dataset_id = "thingspeak"
  project    = "airqo-250220"
  schema     = "[{\"mode\":\"NULLABLE\",\"name\":\"d\",\"type\":\"STRING\"},{\"mode\":\"NULLABLE\",\"name\":\"s\",\"type\":\"STRING\"},{\"mode\":\"NULLABLE\",\"name\":\"p\",\"type\":\"STRING\"},{\"mode\":\"NULLABLE\",\"name\":\"pop\",\"type\":\"INTEGER\"},{\"mode\":\"NULLABLE\",\"name\":\"hhs\",\"type\":\"INTEGER\"},{\"mode\":\"NULLABLE\",\"name\":\"fem_hhs\",\"type\":\"FLOAT\"},{\"mode\":\"NULLABLE\",\"name\":\"long\",\"type\":\"FLOAT\"},{\"mode\":\"NULLABLE\",\"name\":\"lat\",\"type\":\"FLOAT\"},{\"mode\":\"NULLABLE\",\"name\":\"km2\",\"type\":\"FLOAT\"},{\"mode\":\"NULLABLE\",\"name\":\"area\",\"type\":\"FLOAT\"},{\"mode\":\"NULLABLE\",\"name\":\"perimeter\",\"type\":\"FLOAT\"},{\"mode\":\"NULLABLE\",\"name\":\"T123\",\"type\":\"FLOAT\"},{\"mode\":\"NULLABLE\",\"name\":\"not_T123\",\"type\":\"FLOAT\"},{\"mode\":\"NULLABLE\",\"name\":\"light_gas_pc\",\"type\":\"FLOAT\"},{\"mode\":\"NULLABLE\",\"name\":\"light_gas_per_km\",\"type\":\"FLOAT\"},{\"mode\":\"NULLABLE\",\"name\":\"light_lpg_pc\",\"type\":\"FLOAT\"},{\"mode\":\"NULLABLE\",\"name\":\"light_lpg_per_km\",\"type\":\"FLOAT\"},{\"mode\":\"NULLABLE\",\"name\":\"light_biogas_pc\",\"type\":\"FLOAT\"},{\"mode\":\"NULLABLE\",\"name\":\"light_biogas_per_km\",\"type\":\"FLOAT\"},{\"mode\":\"NULLABLE\",\"name\":\"light_par_lantern_pc\",\"type\":\"FLOAT\"},{\"mode\":\"NULLABLE\",\"name\":\"light_par_lantern_per_km\",\"type\":\"FLOAT\"},{\"mode\":\"NULLABLE\",\"name\":\"light_par_tadooba_pc\",\"type\":\"FLOAT\"},{\"mode\":\"NULLABLE\",\"name\":\"light_par_tadooba_per_km\",\"type\":\"FLOAT\"},{\"mode\":\"NULLABLE\",\"name\":\"light_candles_pc\",\"type\":\"FLOAT\"},{\"mode\":\"NULLABLE\",\"name\":\"light_candles_per_km\",\"type\":\"FLOAT\"},{\"mode\":\"NULLABLE\",\"name\":\"light_firewood_pc\",\"type\":\"FLOAT\"},{\"mode\":\"NULLABLE\",\"name\":\"light_firewood_per_km\",\"type\":\"FLOAT\"},{\"mode\":\"NULLABLE\",\"name\":\"light_cow_dung_pc\",\"type\":\"FLOAT\"},{\"mode\":\"NULLABLE\",\"name\":\"light_cow_dung_per_km\",\"type\":\"FLOAT\"},{\"mode\":\"NULLABLE\",\"name\":\"light_grass_pc\",\"type\":\"FLOAT\"},{\"mode\":\"NULLABLE\",\"name\":\"light_grass_per_km\",\"type\":\"FLOAT\"},{\"mode\":\"NULLABLE\",\"name\":\"cook_elec_therm_pc\",\"type\":\"FLOAT\"},{\"mode\":\"NULLABLE\",\"name\":\"cook_elec_therm_per_km\",\"type\":\"FLOAT\"},{\"mode\":\"NULLABLE\",\"name\":\"cook_gas_pc\",\"type\":\"FLOAT\"},{\"mode\":\"NULLABLE\",\"name\":\"cook_gas_per_km\",\"type\":\"FLOAT\"},{\"mode\":\"NULLABLE\",\"name\":\"cook_lpg_pc\",\"type\":\"FLOAT\"},{\"mode\":\"NULLABLE\",\"name\":\"cook_lpg_per_km\",\"type\":\"FLOAT\"},{\"mode\":\"NULLABLE\",\"name\":\"cook_biogas_pc\",\"type\":\"FLOAT\"},{\"mode\":\"NULLABLE\",\"name\":\"cook_biogas_per_km\",\"type\":\"FLOAT\"},{\"mode\":\"NULLABLE\",\"name\":\"cook_par_lantern_pc\",\"type\":\"FLOAT\"},{\"mode\":\"NULLABLE\",\"name\":\"cook_par_lantern_per_km\",\"type\":\"FLOAT\"},{\"mode\":\"NULLABLE\",\"name\":\"cook_charc_pc\",\"type\":\"FLOAT\"},{\"mode\":\"NULLABLE\",\"name\":\"cook_charc_per_km\",\"type\":\"FLOAT\"},{\"mode\":\"NULLABLE\",\"name\":\"cook_firewood_pc\",\"type\":\"FLOAT\"},{\"mode\":\"NULLABLE\",\"name\":\"cook_firewood_per_km\",\"type\":\"FLOAT\"},{\"mode\":\"NULLABLE\",\"name\":\"cook_dung_pc\",\"type\":\"FLOAT\"},{\"mode\":\"NULLABLE\",\"name\":\"cook_dung_per_km\",\"type\":\"FLOAT\"},{\"mode\":\"NULLABLE\",\"name\":\"cook_grass_pc\",\"type\":\"FLOAT\"},{\"mode\":\"NULLABLE\",\"name\":\"cook_grass_per_km\",\"type\":\"FLOAT\"},{\"mode\":\"NULLABLE\",\"name\":\"waste_burn_pc\",\"type\":\"FLOAT\"},{\"mode\":\"NULLABLE\",\"name\":\"waste_burn_per_km\",\"type\":\"FLOAT\"},{\"mode\":\"NULLABLE\",\"name\":\"kitch_outside_built_pc\",\"type\":\"FLOAT\"},{\"mode\":\"NULLABLE\",\"name\":\"kitch_outside_built_per_km\",\"type\":\"FLOAT\"},{\"mode\":\"NULLABLE\",\"name\":\"kitch_make_shift_pc\",\"type\":\"FLOAT\"},{\"mode\":\"NULLABLE\",\"name\":\"kitch_make_shift_per_km\",\"type\":\"FLOAT\"},{\"mode\":\"NULLABLE\",\"name\":\"kitch_open_space_pc\",\"type\":\"FLOAT\"},{\"mode\":\"NULLABLE\",\"name\":\"kitch_open_space_per_km\",\"type\":\"FLOAT\"},{\"mode\":\"NULLABLE\",\"name\":\"pop_density\",\"type\":\"FLOAT\"},{\"mode\":\"NULLABLE\",\"name\":\"hhs_density\",\"type\":\"FLOAT\"},{\"mode\":\"NULLABLE\",\"name\":\"pop_per_hhs\",\"type\":\"FLOAT\"},{\"mode\":\"NULLABLE\",\"name\":\"T123_per_sqkm\",\"type\":\"FLOAT\"},{\"mode\":\"NULLABLE\",\"name\":\"not_T123_per_sqkm\",\"type\":\"FLOAT\"},{\"mode\":\"NULLABLE\",\"name\":\"T123_per_person\",\"type\":\"FLOAT\"},{\"mode\":\"NULLABLE\",\"name\":\"not_T123_per_person\",\"type\":\"FLOAT\"},{\"mode\":\"NULLABLE\",\"name\":\"geometry\",\"type\":\"STRING\"},{\"mode\":\"NULLABLE\",\"name\":\"centroid\",\"type\":\"STRING\"}]"
  table_id   = "geo_census"
}
# terraform import google_bigquery_table.geo_census projects/airqo-250220/datasets/thingspeak/tables/geo_census
