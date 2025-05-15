# modules/database/main.tf - Example module for database abstraction

# This module demonstrates how you could further modularize the database setup
variable "db_type" {
  description = "Type of database (postgres, mariadb, mongodb, influxdb, neo4j, redis)"
  type        = string
}

variable "root_password" {
  description = "Root password for database"
  type        = string
  sensitive   = true
}

variable "port" {
  description = "External port for database"
  type        = number
}

variable "volume_name" {
  description = "Volume name for database data"
  type        = string
}

variable "config_path" {
  description = "Path to config directory"
  type        = string
}

variable "data_path" {
  description = "Path to data directory"
  type        = string
}

variable "secondary_port" {
  description = "Secondary port for database if needed (like Neo4j bolt port)"
  type        = number
  default     = null
}

variable "additional_env" {
  description = "Additional environment variables"
  type        = map(string)
  default     = {}
}

# Docker volume resource
resource "docker_volume" "db_volume" {
  name = var.volume_name
}

# Use local-exec to ensure directories exist
resource "null_resource" "ensure_dirs" {
  provisioner "local-exec" {
    command = "mkdir -p ${var.config_path} ${var.data_path}"
  }
}

# Database container resource - This is a simplified example, each database would need specific configurations
resource "docker_container" "db" {
  name  = var.db_type
  image = "${var.db_type}:latest"
  restart = "unless-stopped"
  
  dynamic "env" {
    for_each = var.additional_env
    content {
      name  = env.key
      value = env.value
    }
  }
  
  volumes {
    volume_name    = docker_volume.db_volume.name
    container_path = "/data"
  }
  
  volumes {
    host_path      = var.config_path
    container_path = "/config"
  }
  
  ports {
    internal = var.db_type == "mariadb" ? 3306 : var.port
    external = var.port
  }
  
  dynamic "ports" {
    for_each = var.secondary_port != null ? [1] : []
    content {
      internal = var.secondary_port
      external = var.secondary_port
    }
  }
  
  depends_on = [
    null_resource.ensure_dirs,
    docker_volume.db_volume
  ]
}

output "container_id" {
  value = docker_container.db.id
}

output "container_name" {
  value = docker_container.db.name
}

output "container_ip" {
  value = docker_container.db.network_data[0].ip_address
}