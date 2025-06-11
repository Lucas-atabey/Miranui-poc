terraform {
  required_providers {
    ionoscloud = {
      source  = "ionos-cloud/ionoscloud"
      version = ">= 6.4.10"
    }
  }
}

terraform {
  backend "s3" {
    bucket                      = "lucas-terraform"
    key                         = "state/terraform.tfstate"
    region                      = "us-east-1" # Random us region not used for ovh backend
    endpoints                   = { s3 = "https://s3.rbx.io.cloud.ovh.net" }
    access_key                  = var.access_key
    secret_key                  = var.secret_key
    skip_credentials_validation = true
    skip_metadata_api_check     = true
    use_path_style              = true
    skip_region_validation      = true
    skip_requesting_account_id  = true
    skip_s3_checksum            = true
  }
}

provider "ionoscloud" {
  token = var.ionos_token
}

resource "ionoscloud_datacenter" "main" {
  location            = "fr/par"
  name                = "Lucas Data Center"
  description         = "test"
  sec_auth_protection = false
}
