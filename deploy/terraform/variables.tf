variable "ionos_token" {
  description = "IONOS API token"
  type        = string
  sensitive   = true
}

variable "access_key" {
  description = "IONOS S3 access key"
  type        = string
  sensitive   = true
}

variable "secret_key" {
  description = "IONOS S3 secret key"
  type        = string
  sensitive   = true
}
