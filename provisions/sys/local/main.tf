# main.tf - Main Terraform configuration file

terraform {
  required_providers {
    docker = {
      source  = "kreuzwerker/docker"
      version = "~> 3.0.0"
    }
    null = {
      source = "hashicorp/null"
      version = "~> 3.2.0"
    }
    random = {
      source = "hashicorp/random"
      version = "~> 3.5.0"
    }
  }
  required_version = ">= 1.0.0"
}

provider "docker" { }

# Generate random token for InfluxDB
resource "random_password" "influxdb_token" {
  count   = var.create_influxdb_token ? 1 : 0
  length  = 32
  special = false
}

locals {
  influxdb_token = var.create_influxdb_token ? random_password.influxdb_token[0].result : "default-token"
  root_dir       = "${path.module}/dbstack"
  config_dir     = "${local.root_dir}/config"
  secrets_dir    = "${local.root_dir}/secrets"
  logs_dir       = "${local.root_dir}/logs"
  data_dir       = "${local.root_dir}/data"
}

# Create necessary directories
resource "null_resource" "create_directories" {
  provisioner "local-exec" {
    command = <<-EOT
      mkdir -p ${local.config_dir}/{postgres,mariadb,mongodb,influxdb,neo4j,redis}
      mkdir -p ${local.secrets_dir}
      mkdir -p ${local.logs_dir}
      mkdir -p ${local.data_dir}/{postgres,mariadb,mongodb,mongodb-log,influxdb,neo4j,redis}
      chmod 700 ${local.secrets_dir}
    EOT
  }
}

# Create secrets files
resource "null_resource" "create_secrets" {
  depends_on = [null_resource.create_directories]

  provisioner "local-exec" {
    command = <<-EOT
      echo "admin" > ${local.secrets_dir}/influxdb2-admin-username
      echo "${var.root_password}" > ${local.secrets_dir}/influxdb2-admin-password
      echo "${local.influxdb_token}" > ${local.secrets_dir}/influxdb2-admin-token
      echo "neo4j/${var.root_password}" > ${local.secrets_dir}/neo4j_auth.txt
      chmod 600 ${local.secrets_dir}/*
    EOT
  }
}

# Create MongoDB init script
resource "null_resource" "mongodb_init_script" {
  depends_on = [null_resource.create_directories]

  provisioner "local-exec" {
    command = <<-EOT
      mkdir -p ${local.root_dir}/mongodb/initdb.d
      cat > ${local.root_dir}/mongodb/initdb.d/mongo-init.js <<EOF
// MongoDB initialization script
db.createUser({
  user: 'appuser',
  pwd: '${var.root_password}',
  roles: [{ role: 'readWrite', db: 'application' }]
});
EOF
    EOT
  }
}

# Create env file
resource "null_resource" "create_env_file" {
  depends_on = [null_resource.create_directories]

  provisioner "local-exec" {
    command = <<-EOT
      cat > ${local.root_dir}/.env <<EOF
DB_ROOT_PASSWORD=${var.root_password}
INFLUXDB_TOKEN=${local.influxdb_token}
EOF
      chmod 600 ${local.root_dir}/.env
    EOT
  }
}

# Docker volumes
resource "docker_volume" "postgres_data" {
  name = "postgres-data"
}

resource "docker_volume" "mariadb_data" {
  name = "mariadb-data"
}

resource "docker_volume" "mongodb_data" {
  name = "mongodb-data"
}

resource "docker_volume" "influxdb_data" {
  name = "influxdb2-data"
}

resource "docker_volume" "influxdb_config" {
  name = "influxdb2-config"
}

# Create Docker containers
resource "docker_container" "postgres" {
  name  = "postgres"
  image = "postgres:latest"
  restart = "unless-stopped"
  
  env = [
    "POSTGRES_USER=postgres",
    "POSTGRES_PASSWORD=${var.root_password}"
  ]
  
  volumes {
    volume_name    = docker_volume.postgres_data.name
    container_path = "/var/lib/postgresql/data"
  }
  
  volumes {
    host_path      = "${local.config_dir}/postgres"
    container_path = "/etc/postgresql/conf.d"
  }
  
  ports {
    internal = 5432
    external = 5432
  }
  
  healthcheck {
    test     = ["CMD-SHELL", "pg_isready -U postgres"]
    interval = "10s"
    timeout  = "5s"
    retries  = 5
  }

  depends_on = [
    null_resource.create_directories,
    docker_volume.postgres_data
  ]
}

resource "docker_container" "mariadb" {
  name  = "mariadb"
  image = "mariadb:10.5"
  restart = "unless-stopped"
  command = ["mysqld", "--innodb-flush-method=fsync", "--transaction-isolation=READ-COMMITTED", "--binlog-format=ROW"]
  
  env = [
    "MYSQL_ROOT_PASSWORD=${var.root_password}",
    "MYSQL_DATABASE=appwrite",
    "MYSQL_USER=user",
    "MYSQL_PASSWORD=${var.root_password}"
  ]
  
  volumes {
    volume_name    = docker_volume.mariadb_data.name
    container_path = "/var/lib/mysql"
  }
  
  volumes {
    host_path      = "${local.config_dir}/mariadb"
    container_path = "/etc/mysql/conf.d"
  }
  
  ports {
    internal = 3306
    external = 3307
  }
  
  healthcheck {
    test     = ["CMD", "mysqladmin", "ping", "-h", "localhost", "-u", "root", "-p${var.root_password}"]
    interval = "10s"
    timeout  = "5s"
    retries  = 5
  }

  depends_on = [
    null_resource.create_directories,
    docker_volume.mariadb_data
  ]
}

resource "docker_container" "mongodb" {
  name  = "mongodb"
  image = "mongo:latest"
  restart = "unless-stopped"
  
  env = [
    "MONGO_INITDB_ROOT_USERNAME=root",
    "MONGO_INITDB_ROOT_PASSWORD=${var.root_password}"
  ]
  
  volumes {
    volume_name    = docker_volume.mongodb_data.name
    container_path = "/data/db"
  }
  
  volumes {
    host_path      = "${local.root_dir}/mongodb/initdb.d/mongo-init.js"
    container_path = "/docker-entrypoint-initdb.d/mongo-init.js"
    read_only      = true
  }
  
  volumes {
    host_path      = "${local.data_dir}/mongodb-log"
    container_path = "/var/log/mongodb"
  }
  
  volumes {
    host_path      = "${local.config_dir}/mongodb"
    container_path = "/etc/mongo"
  }
  
  ports {
    internal = 27017
    external = 27017
  }
  
  healthcheck {
    test     = ["CMD", "echo", "'db.runCommand(\"ping\").ok'", "|", "mongosh", "mongodb:27017/test", "--quiet"]
    interval = "10s"
    timeout  = "5s"
    retries  = 5
  }

  depends_on = [
    null_resource.create_directories,
    null_resource.mongodb_init_script,
    docker_volume.mongodb_data
  ]
}

resource "docker_container" "influxdb" {
  name  = "influxdb"
  image = "influxdb:2"
  restart = "unless-stopped"
  
  env = [
    "DOCKER_INFLUXDB_INIT_MODE=setup",
    "DOCKER_INFLUXDB_INIT_USERNAME_FILE=/run/secrets/influxdb2-admin-username",
    "DOCKER_INFLUXDB_INIT_PASSWORD_FILE=/run/secrets/influxdb2-admin-password",
    "DOCKER_INFLUXDB_INIT_ADMIN_TOKEN_FILE=/run/secrets/influxdb2-admin-token",
    "DOCKER_INFLUXDB_INIT_ORG=itlc",
    "DOCKER_INFLUXDB_INIT_BUCKET=b0"
  ]
  
  volumes {
    volume_name    = docker_volume.influxdb_data.name
    container_path = "/var/lib/influxdb2"
  }
  
  volumes {
    host_path      = "${local.config_dir}/influxdb"
    container_path = "/etc/influxdb2"
  }
  
  volumes {
    host_path      = "${local.secrets_dir}/influxdb2-admin-username"
    container_path = "/run/secrets/influxdb2-admin-username"
    read_only      = true
  }
  
  volumes {
    host_path      = "${local.secrets_dir}/influxdb2-admin-password"
    container_path = "/run/secrets/influxdb2-admin-password"
    read_only      = true
  }
  
  volumes {
    host_path      = "${local.secrets_dir}/influxdb2-admin-token"
    container_path = "/run/secrets/influxdb2-admin-token"
    read_only      = true
  }
  
  ports {
    internal = 8086
    external = 8086
  }
  
  healthcheck {
    test     = ["CMD", "curl", "-f", "http://localhost:8086/health"]
    interval = "30s"
    timeout  = "10s"
    retries  = 5
  }

  depends_on = [
    null_resource.create_directories,
    null_resource.create_secrets,
    docker_volume.influxdb_data,
    docker_volume.influxdb_config
  ]
}

resource "docker_container" "neo4j" {
  name  = "neo4j"
  image = "neo4j:latest"
  restart = "unless-stopped"
  
  env = [
    "NEO4J_AUTH_FILE=/run/secrets/neo4j_auth_file"
  ]
  
  volumes {
    host_path      = "${local.data_dir}/neo4j/logs"
    container_path = "/logs"
  }
  
  volumes {
    host_path      = "${local.data_dir}/neo4j/data"
    container_path = "/data"
  }
  
  volumes {
    host_path      = "${local.data_dir}/neo4j/plugins"
    container_path = "/plugins"
  }
  
  volumes {
    host_path      = "${local.config_dir}/neo4j"
    container_path = "/config"
  }
  
  volumes {
    host_path      = "${local.secrets_dir}/neo4j_auth.txt"
    container_path = "/run/secrets/neo4j_auth_file"
    read_only      = true
  }
  
  ports {
    internal = 7474
    external = 7474
  }
  
  ports {
    internal = 7687
    external = 7687
  }
  
  healthcheck {
    test     = ["CMD", "cypher-shell", "-u", "neo4j", "-p", "${var.root_password}", "RETURN 1"]
    interval = "30s"
    timeout  = "10s"
    retries  = 5
  }

  depends_on = [
    null_resource.create_directories,
    null_resource.create_secrets
  ]
}

resource "docker_container" "redis" {
  name  = "redis"
  image = "redis:6.2-alpine"
  restart = "unless-stopped"
  command = ["redis-server", "--save", "20", "1", "--loglevel", "warning", "--requirepass", "${var.root_password}"]
  
  volumes {
    host_path      = "${local.data_dir}/redis"
    container_path = "/data"
  }
  
  volumes {
    host_path      = "${local.config_dir}/redis"
    container_path = "/usr/local/etc/redis"
  }
  
  ports {
    internal = 6379
    external = 6379
  }
  
  healthcheck {
    test     = ["CMD", "redis-cli", "ping"]
    interval = "10s"
    timeout  = "5s"
    retries  = 5
  }

  depends_on = [
    null_resource.create_directories
  ]
}
