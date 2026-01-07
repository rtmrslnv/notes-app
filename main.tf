terraform {
  required_providers {
    yandex = {
      source = "yandex-cloud/yandex"
    }
  }
}

provider "yandex" {
  cloud_id  = "CHANGEME"
  folder_id = "CHANGEME"
  zone      = "ru-central1-a"
  service_account_key_file = "service_account_key_file.json"
}

resource "yandex_compute_disk" "notes-db-disk" {
    name = "notes-db-disk"
    type = "network-hdd"
    zone = "ru-central1-a"
    size = 15
}

resource "yandex_compute_instance" "vm-1" {
  name        = "notes-app-vm"
  platform_id = "standard-v1"
  zone        = "ru-central1-a"
  timeouts {
    create = "20m"
  }

  resources {
    cores  = 2
    memory = 2
    core_fraction = 20
  }

  boot_disk {
    initialize_params {
      image_id = "fd8j5voj4pc21791fc8o"
    }
  }

  secondary_disk {
    disk_id = yandex_compute_disk.notes-db-disk.id
    device_name = "notes-db-disk"
  }

  network_interface {
    subnet_id = yandex_vpc_subnet.subnet-1.id
    nat       = true
  }

  metadata = {
    ssh-keys = "ubuntu:${file("~/.ssh/id_rsa.pub")}"
    user-data = "${file("./cloud-config")}"
  }
}

resource "yandex_storage_bucket" "notes-static-bucket" {
  bucket = "notes-static-bucket"
  max_size = 1073741824
  anonymous_access_flags {
    read        = true
    list        = false
    config_read = false
  }
}

resource "yandex_storage_object" "static-styles" {
  bucket = yandex_storage_bucket.notes-static-bucket.bucket
  key    = "styles.css"
  source = "./app/static/styles.css"
  content_type = "text/css"
}

resource "yandex_vpc_network" "network-1" {
  name = "notes-app-network"
}

resource "yandex_vpc_subnet" "subnet-1" {
  name           = "notes-app-network-subnet"
  zone           = "ru-central1-a"
  network_id     = yandex_vpc_network.network-1.id
  v4_cidr_blocks = ["10.2.0.0/16"]
}

output "internal_ip_address_vm_1" {
  value = yandex_compute_instance.vm-1.network_interface.0.ip_address
}

output "external_ip_address_vm_1" {
  value = yandex_compute_instance.vm-1.network_interface.0.nat_ip_address
}