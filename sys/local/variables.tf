# variables.tf - Terraform variables definition file

variable "root_password" {
  description = "Root password for database services"
  type        = string
  default     = "password"
  sensitive   = true

  validation {
    condition     = length(var.root_password) >= 8
    error_message = "Password must be at least 8 characters long."
  }
}

variable "create_influxdb_token" {
  description = "Generate a random token for InfluxDB"
  type        = bool
  default     = true
}

variable "postgres_port" {
  description = "Port for PostgreSQL"
  type        = number
  default     = 5432
}

variable "mariadb_port" {
  description = "Port for MariaDB"
  type        = number
  default     = 3307
}

variable "mongodb_port" {
  description = "Port for MongoDB"
  type        = number
  default     = 27017
}

variable "influxdb_port" {
  description = "Port for InfluxDB"
  type        = number
  description = "Port for InfluxDB"
  type        = number
  default     = 8086
}

variable "neo4j_browser_port" {
  description = "Port for Neo4j Browser"
  type        = number
  default     = 7474
}

variable "neo4j_bolt_port" {
  description = "Port for Neo4j Bolt protocol"
  type        = number
  default     = 7687
}

variable "redis_port" {
  description = "Port for Redis"
  type        = number
  default     = 6379
}

variable "influxdb_org" {
  description = "Organization name for InfluxDB"
  type        = string
  default     = "itlc"
}

variable "influxdb_bucket" {
  description = "Default bucket name for InfluxDB"
  type        = string
  default     = "b0"
}

variable "mongodb_database" {
  description = "Default database name for MongoDB application user"
  type        = string
  default     = "application"
}

variable "mariadb_database" {
  description = "Default database name for MariaDB"
  type        = string
  default     = "appwrite"
}

variable "mariadb_user" {
  description = "Default user for MariaDB"
  type        = string
  default     = "user"
}

variable "mongodb_user" {
  description = "Application user for MongoDB"
  type        = string
  default     = "appuser"
}