terraform {
  required_providers {
    ionoscloud = {
      source  = "ionos-cloud/ionoscloud"
      version = ">= 6.4.10"
    }
  }
  backend "s3" {
    bucket                      = "lucas-terraform"
    key                         = "state/terraform.tfstate"
    region                      = "us-east-1" # Random us region not used for ovh backend
    endpoints                   = { s3 = "https://s3.rbx.io.cloud.ovh.net" }
    skip_credentials_validation = true
    skip_metadata_api_check     = true
    use_path_style              = true
    skip_region_validation      = true
    skip_requesting_account_id  = true
    skip_s3_checksum            = true
  }
}


provider "ionoscloud" {
  token         = var.ionos_token
  s3_access_key = var.ionos_s3_access_key
  s3_secret_key = var.ionos_s3_secret_key
}

resource "ionoscloud_datacenter" "main" {
  location            = "fr/par"
  name                = "Lucas Data Center"
  description         = "test"
  sec_auth_protection = false
}

resource "ionoscloud_lan" "mariadb" {
  datacenter_id = ionoscloud_datacenter.main.id
  public        = false
  name          = "Lucas Lan Maria db"
}

locals {
  # Une IP privée correcte
  database_ip_cidr = "10.7.222.11/23"
}

resource "ionoscloud_mariadb_cluster" "example" {
  mariadb_version = "10.11"
  location        = "fr/par"
  instances       = 1
  cores           = 1
  ram             = 4
  storage_size    = 10
  display_name    = "MariaDB_cluster"

  connections {
    datacenter_id = ionoscloud_datacenter.main.id
    lan_id        = ionoscloud_lan.mariadb.id
    cidr          = local.database_ip_cidr
  }

  credentials {
    username = "username"
    password = "username17@"
  }

  maintenance_window {
    day_of_the_week = "Sunday"
    time            = "09:00:00"
  }
}

resource "ionoscloud_ipblock" "example" {
  location = ionoscloud_datacenter.main.location
  size     = 1
  name     = "Lucas static IP"
}

resource "ionoscloud_lan" "public" {
  datacenter_id = ionoscloud_datacenter.main.id
  public        = true
  name          = "Lucas Lan"
}

resource "ionoscloud_server" "example" {
  name                = "Lucas Dedicated Core Server"
  datacenter_id       = ionoscloud_datacenter.main.id
  cores               = 2
  ram                 = 4096
  image_name          = data.ionoscloud_image.example.name
  security_groups_ids = []
  availability_zone   = "AUTO"
  cpu_family          = "INTEL_ICELAKE"
}

resource "ionoscloud_nic" "public" {
  datacenter_id   = ionoscloud_datacenter.main.id
  server_id       = ionoscloud_server.example.id
  lan             = ionoscloud_lan.public.id
  name            = "Lucas NIC public"
  dhcp            = true
  firewall_active = false
  ips             = [ionoscloud_ipblock.example.ips[0]]
}

resource "ionoscloud_nic" "private" {
  datacenter_id   = ionoscloud_datacenter.main.id
  server_id       = ionoscloud_server.example.id
  lan             = ionoscloud_lan.mariadb.id
  name            = "Lucas Private NIC"
  dhcp            = true
  firewall_active = false
}

data "ionoscloud_image" "example" {
  type        = "HDD"
  cloud_init  = "V1"
  image_alias = "ubuntu:latest"
  location    = "us/ewr"
}

resource "ionoscloud_volume" "example" {
  server_id         = ionoscloud_server.example.id
  datacenter_id     = ionoscloud_datacenter.main.id
  name              = "Lucas HDD Storage"
  size              = 10
  disk_type         = "HDD"
  availability_zone = "AUTO"
  bus               = "VIRTIO"
  image_name        = data.ionoscloud_image.example.name
  ssh_key_path      = ["files/id_ed25519.pub"]
  user_data         = base64encode(file("${path.module}/files/cloud-init.yaml"))
}

resource "ionoscloud_container_registry" "example" {
  garbage_collection_schedule {
    days = ["Monday", "Tuesday"]
    time = "05:19:00+00:00"
  }
  location = "de/fra"
  name     = "lucas-rex"
  features {
    vulnerability_scanning = true
  }
}
