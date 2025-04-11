# outputs.tf - Terraform outputs definition file

output "postgres_connection" {
  description = "PostgreSQL connection information"
  value       = "PostgreSQL is available at localhost:${var.postgres_port} with username 'postgres' and the configured password"
}

output "mariadb_connection" {
  description = "MariaDB connection information"
  value       = "MariaDB is available at localhost:${var.mariadb_port} with username 'root' and the configured password"
}

output "mongodb_connection" {
  description = "MongoDB connection information"
  value       = "MongoDB is available at localhost:${var.mongodb_port} with username 'root' and the configured password"
}

output "influxdb_connection" {
  description = "InfluxDB connection information"
  value       = "InfluxDB is available at http://localhost:${var.influxdb_port} with username 'admin' and the configured password"
}

output "influxdb_token" {
  description = "InfluxDB admin token"
  value       = local.influxdb_token
  sensitive   = true
}

output "neo4j_connection" {
  description = "Neo4j connection information"
  value       = "Neo4j is available at http://localhost:${var.neo4j_browser_port} with username 'neo4j' and the configured password. Bolt port is ${var.neo4j_bolt_port}."
}

output "redis_connection" {
  description = "Redis connection information"
  value       = "Redis is available at localhost:${var.redis_port} with the configured password"
}

output "all_services_status" {
  description = "Status of all database services"
  value       = "Run './db_mng_trfm.sh -a t' to check the status of all services"
}

output "backup_instructions" {
  description = "Instructions for backing up databases"
  value       = "Run './db_mng_trfm.sh -a b' to backup all databases, or './db_mng_trfm.sh -<service_initial> b' for a specific service"
}