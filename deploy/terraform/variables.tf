variable "ionos_token" {
  description = "IONOS API token"
  type        = string
  sensitive   = true
}

variable "ionos_s3_access_key" {
  type      = string
  sensitive = true
}

variable "ionos_s3_secret_key" {
  type      = string
  sensitive = true
}
