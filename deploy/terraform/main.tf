terraform {
  required_providers {
    ionoscloud = {
      source  = "ionos-cloud/ionoscloud"
      version = ">= 6.4.10"
    }
  }
}

provider "ionoscloud" {
  token = var.ionos_token
}

resource "ionoscloud_datacenter" "main" {
  location            = "fr/par"
  name                = "Lucas Data Center"
  sec_auth_protection = false
}
