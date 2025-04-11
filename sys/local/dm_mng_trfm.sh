#!/bin/bash
# db_helpers.sh - Helper functions for database management with Terraform

# Script variables
CONFIG_DIR="${ROOT_DIR:-./dbstack}/config"
DATA_DIR="${ROOT_DIR:-./dbstack}/data"

# Create a basic database configuration file
create_db_config() {
  local db_type=$1
  local config_file=$2
  local content=$3
  
  mkdir -p "${CONFIG_DIR}/${db_type}"
  echo "$content" > "${CONFIG_DIR}/${db_type}/$config_file"
  echo "Created config file: ${CONFIG_DIR}/${db_type}/$config_file"
}

# Generate example configurations for each database type
generate_example_configs() {
  # PostgreSQL example config
  create_db_config "postgres" "postgresql.conf" "
# PostgreSQL Configuration
max_connections = 100
shared_buffers = 128MB
dynamic_shared_memory_type = posix
max_wal_size = 1GB
min_wal_size = 80MB
log_timezone = 'UTC'
datestyle = 'iso, mdy'
timezone = 'UTC'
  "

  # MariaDB example config
  create_db_config "mariadb" "custom.cnf" "
[mysqld]
innodb_buffer_pool_size = 256M
innodb_log_file_size = 64M
max_connections = 100
character-set-server = utf8mb4
collation-server = utf8mb4_unicode_ci
  "

  # MongoDB example config
  create_db_config "mongodb" "mongod.conf" "
# MongoDB Configuration
storage:
  dbPath: /data/db
  journal:
    enabled: true
systemLog:
  destination: file
  path: /var/log/mongodb/mongod.log
  logAppend: true
net:
  port: 27017
  bindIp: 0.0.0.0
processManagement:
  timeZoneInfo: /usr/share/zoneinfo
  "

  # InfluxDB example config
  create_db_config "influxdb" "influxdb.conf" "
# InfluxDB configuration
[meta]
  dir = \"/var/lib/influxdb/meta\"

[data]
  dir = \"/var/lib/influxdb/data\"
  wal-dir = \"/var/lib/influxdb/wal\"
  "

  # Neo4j example config
  create_db_config "neo4j" "neo4j.conf" "
# Neo4j Config
dbms.memory.heap.initial_size=512m
dbms.memory.heap.max_size=1G
dbms.memory.pagecache.size=512m
  "

  # Redis example config
  create_db_config "redis" "redis.conf" "
# Redis configuration
maxmemory 256mb
maxmemory-policy allkeys-lru
  "

  echo "Example configurations generated in $CONFIG_DIR"
}

# Database backup helpers
backup_postgres() {
  local backup_dir="$1"
  local timestamp="$2"
  local password="$3"
  
  PGPASSWORD="$password" pg_dump -h localhost -U postgres postgres > "$backup_dir/postgres_$timestamp.sql"
  echo "PostgreSQL backup created: $backup_dir/postgres_$timestamp.sql"
}

backup_mariadb() {
  local backup_dir="$1"
  local timestamp="$2"
  local password="$3"
  local database="${4:-appwrite}"
  
  mysqldump -h 127.0.0.1 -P 3307 -u root -p"$password" "$database" > "$backup_dir/mariadb_$timestamp.sql"
  echo "MariaDB backup created: $backup_dir/mariadb_$timestamp.sql"
}

# Import a database backup
import_backup() {
  local db_type="$1"
  local backup_file="$2"
  local password="$3"
  
  case "$db_type" in
    postgres)
      PGPASSWORD="$password" psql -h localhost -U postgres postgres < "$backup_file"
      ;;
    mariadb)
      mysql -h 127.0.0.1 -P 3307 -u root -p"$password" < "$backup_file"
      ;;
    mongodb)
      mongorestore --host localhost --port 27017 -u root -p "$password" --authenticationDatabase admin "$backup_file"
      ;;
    *)
      echo "Import not implemented for $db_type"
      return 1
      ;;
  esac
  
  echo "Import completed for $db_type from $backup_file"
}

# Database monitoring function
monitor_database() {
  local db_type="$1"
  local interval="${2:-5}"  # Default to 5 seconds
  local duration="${3:-60}" # Default to 60 seconds
  local password="$4"
  
  echo "Monitoring $db_type for $(($duration / 60)) minutes with ${interval}s intervals"
  
  count=$(($duration / $interval))
  for ((i=1; i<=count; i++)); do
    case "$db_type" in
      postgres)
        echo "--- PostgreSQL Stats ($(date)) ---"
        PGPASSWORD="$password" psql -h localhost -U postgres -c "SELECT count(*) FROM pg_stat_activity;"
        ;;
      redis)
        echo "--- Redis Stats ($(date)) ---"
        redis-cli -h localhost -p 6379 -a "$password" INFO | grep connected_clients
        redis-cli -h localhost -p 6379 -a "$password" INFO | grep used_memory_human
        ;;
      # Add more database types as needed
    esac
    
    sleep $interval
  done
}

# Create test data for a database
create_test_data() {
  local db_type="$1"
  local password="$2"
  
  echo "Creating test data for $db_type..."
  
  case "$db_type" in
    postgres)
      PGPASSWORD="$password" psql -h localhost -U postgres postgres <<EOF
CREATE TABLE IF NOT EXISTS test_data (
  id SERIAL PRIMARY KEY,
  name VARCHAR(100),
  value TEXT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO test_data (name, value) VALUES 
('test1', 'This is a test value 1'),
('test2', 'This is a test value 2'),
('test3', 'This is a test value 3');
EOF
      ;;
    mariadb)
      mysql -h 127.0.0.1 -P 3307 -u root -p"$password" <<EOF
CREATE DATABASE IF NOT EXISTS test;
USE test;
CREATE TABLE IF NOT EXISTS test_data (
  id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(100),
  value TEXT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO test_data (name, value) VALUES 
('test1', 'This is a test value 1'),
('test2', 'This is a test value 2'),
('test3', 'This is a test value 3');
EOF
      ;;
    # Add more database types as needed
  esac
  
  echo "Test data created for $db_type"
}

# Function to display database resource usage
show_db_resource_usage() {
  local db_type="$1"
  
  echo "Resource usage for $db_type:"
  docker stats --no-stream "$db_type"
}

# Function to rotate logs
rotate_logs() {
  local logs_dir="${ROOT_DIR:-./dbstack}/logs"
  local retention_days="${1:-7}"
  
  echo "Rotating logs, keeping $retention_days days of history"
  find "$logs_dir" -name "*.log" -type f -mtime +$retention_days -delete
  
  # Create new log files if needed
  for db in postgres mariadb mongodb influxdb neo4j redis; do
    if docker ps -q -f name=$db > /dev/null; then
      docker logs $db > "$logs_dir/${db}_$(date +%Y%m%d_%H%M%S).log"
    fi
  done
  
  echo "Log rotation complete"
}

# Test database connections
test_connections() {
  local password="$1"
  
  echo "Testing database connections..."
  
  # PostgreSQL
  if docker ps -q -f name=postgres > /dev/null; then
    if PGPASSWORD="$password" psql -h localhost -U postgres -c "SELECT 1" > /dev/null 2>&1; then
      echo "PostgreSQL: Connection successful ✅"
    else
      echo "PostgreSQL: Connection failed ❌"
    fi
  fi
  
  # MariaDB
  if docker ps -q -f name=mariadb > /dev/null; then
    if mysql -h 127.0.0.1 -P 3307 -u root -p"$password" -e "SELECT 1" > /dev/null 2>&1; then
      echo "MariaDB: Connection successful ✅"
    else
      echo "MariaDB: Connection failed ❌"
    fi
  fi
  
  # More databases can be added as needed
  
  echo "Connection tests completed"
}