#!/bin/bash
# dbctl.sh - Database Stack Management Script for Terraform

# Default directory is current directory if not specified
TF_DIR="$(pwd)"
ROOT_DIR="$(pwd)/dbstack"
CONFIG_DIR="$ROOT_DIR/config"
SECRETS_DIR="$ROOT_DIR/secrets"
LOGS_DIR="$ROOT_DIR/logs"
DATA_DIR="$ROOT_DIR/data"
BACKUP_DIR="$ROOT_DIR/backups"
DEFAULT_ROOT_PASSWORD="password"

# Load environment variables from .env file
load_env() {
  if [ -f "$ROOT_DIR/.env" ]; then
    export $(grep -v '^#' "$ROOT_DIR/.env" | xargs)
  fi
}

# Set the Terraform directory
set_tf_dir() {
  local dir="$1"
  
  if [ -n "$dir" ]; then
    # Convert to absolute path if relative
    if [[ "$dir" != /* ]]; then
      dir="$(pwd)/$dir"
    fi
    
    if [ ! -d "$dir" ]; then
      echo "❌ Directory does not exist: $dir"
      exit 1
    fi
    
    TF_DIR="$dir"
    echo "✅ Using Terraform directory: $TF_DIR"
  fi
}

# Initialize or apply Terraform configuration
init_stack() {
  local root_password="${1:-$DEFAULT_ROOT_PASSWORD}"
  
  if [ "$root_password" == "$DEFAULT_ROOT_PASSWORD" ]; then
    echo "⚠️ Warning: Using default password. For production environments, provide a strong password."
  elif [ ${#root_password} -lt 8 ]; then
    echo "⚠️ Warning: Password is less than 8 characters. Consider using a stronger password."
  fi

  # Change to Terraform directory
  cd "$TF_DIR" || exit 1

  # Create main.tf if not exists (terraform configuration)
  if [ ! -f "main.tf" ]; then
    echo "🔄 Creating Terraform configuration file..."
    # You would need the actual content of main.tf here
    echo "Please ensure main.tf exists in the directory: $TF_DIR"
    exit 1
  fi

  echo "🔄 Initializing Terraform in $TF_DIR..."
  terraform init

  echo "🔄 Applying Terraform configuration with custom root password..."
  terraform apply -var="root_password=$root_password" -auto-approve

  echo "✅ Stack initialized with Terraform"
}

# Backup database
backup_database() {
  local service="$1"
  local timestamp=$(date +"%Y%m%d_%H%M%S")
  local backup_dir="$BACKUP_DIR/$service"
  
  load_env
  local root_password="${DB_ROOT_PASSWORD:-$DEFAULT_ROOT_PASSWORD}"
  
  mkdir -p "$backup_dir"
  
  case "$service" in
    postgres)
      docker exec postgres pg_dump -U postgres postgres > "$backup_dir/postgres_$timestamp.sql"
      ;;
    mariadb)
      docker exec mariadb mysqldump -u root -p"$root_password" appwrite > "$backup_dir/mariadb_$timestamp.sql"
      ;;
    mongodb)
      docker exec mongodb mongodump --username root --password "$root_password" --authenticationDatabase admin --out /tmp/mongodump
      docker cp mongodb:/tmp/mongodump "$backup_dir/mongodb_$timestamp"
      ;;
    influxdb)
      local token="${INFLUXDB_TOKEN}"
      local org="itlc"
      local bucket="b0"
      echo "Creating InfluxDB backup..."
      docker exec influxdb influx backup /tmp/influxdb-backup -t $token --org $org
      docker cp influxdb:/tmp/influxdb-backup "$backup_dir/influxdb_$timestamp"
      ;;
    neo4j)
      echo "Creating Neo4j backup..."
      docker exec neo4j neo4j-admin dump --database=neo4j --to=/tmp/neo4j.dump
      docker cp neo4j:/tmp/neo4j.dump "$backup_dir/neo4j_$timestamp.dump"
      ;;
    redis)
      echo "Creating Redis backup..."
      docker exec redis redis-cli -a "$root_password" SAVE
      docker cp redis:/data/dump.rdb "$backup_dir/redis_$timestamp.rdb"
      ;;
    *)
      echo "Unknown service: $service"
      return 1
      ;;
  esac
  
  echo "✅ Backed up $service to $backup_dir"
}

# Check health of a service
check_health() {
  local service="$1"
  local container_name
  
  case "$service" in
    postgres) container_name="postgres" ;;
    mariadb) container_name="mariadb" ;;
    mongodb) container_name="mongodb" ;;
    influxdb) container_name="influxdb" ;;
    neo4j) container_name="neo4j" ;;
    redis) container_name="redis" ;;
    *)
      echo "Unknown service: $service"
      return 1
      ;;
  esac
  
  if ! docker ps | grep -q "$container_name"; then
    echo "❌ $service is not running"
    return 1
  fi
  
  echo "Checking $service health..."
  docker inspect --format='{{json .State.Health}}' "$container_name" | jq
}

# Connect to database CLI
connect_cli() {
  local service="$1"
  
  load_env
  local root_password="${DB_ROOT_PASSWORD:-$DEFAULT_ROOT_PASSWORD}"
  local influx_token="${INFLUXDB_TOKEN}"
  
  case "$service" in
    postgres)
      docker exec -it postgres psql -U postgres
      ;;
    mariadb)
      docker exec -it mariadb mysql -u root -p"$root_password"
      ;;
    mongodb)
      docker exec -it mongodb mongosh -u root -p "$root_password" --authenticationDatabase admin
      ;;
    influxdb)
      echo "Connecting to InfluxDB CLI..."
      echo "Token: $influx_token"
      echo "Use this token when prompted or add to your command with -t"
      docker exec -it influxdb influx
      ;;
    neo4j)
      echo "Connecting to Neo4j Browser at http://localhost:7474"
      echo "Username: neo4j"
      echo "Password: $root_password"
      echo "Or use cypher-shell:"
      docker exec -it neo4j cypher-shell -u neo4j -p "$root_password"
      ;;
    redis)
      docker exec -it redis redis-cli -a "$root_password"
      ;;
    *)
      echo "Unknown service: $service"
      return 1
      ;;
  esac
}

# Show statistics for a service
show_stats() {
  local service="$1"
  
  load_env
  local root_password="${DB_ROOT_PASSWORD:-$DEFAULT_ROOT_PASSWORD}"
  local influx_token="${INFLUXDB_TOKEN}"
  
  case "$service" in
    postgres)
      echo "PostgreSQL Stats:"
      docker exec postgres psql -U postgres -c "SELECT pg_database.datname, pg_size_pretty(pg_database_size(pg_database.datname)) AS size FROM pg_database;"
      docker exec postgres psql -U postgres -c "SELECT count(*) FROM pg_stat_activity;"
      ;;
    mariadb)
      echo "MariaDB Stats:"
      docker exec mariadb mysql -u root -p"$root_password" -e "SHOW STATUS LIKE '%Conn%';"
      docker exec mariadb mysql -u root -p"$root_password" -e "SELECT table_schema, ROUND(SUM(data_length + index_length) / 1024 / 1024, 2) 'Size (MB)' FROM information_schema.tables GROUP BY table_schema;"
      ;;
    mongodb)
      echo "MongoDB Stats:"
      docker exec mongodb mongosh -u root -p "$root_password" --authenticationDatabase admin --eval "db.serverStatus().connections"
      docker exec mongodb mongosh -u root -p "$root_password" --authenticationDatabase admin --eval "db.stats()"
      ;;
    influxdb)
      echo "InfluxDB Stats:"
      docker exec influxdb influx bucket list --token $influx_token
      echo "Organizations:"
      docker exec influxdb influx org list --token $influx_token
      echo "Usage stats might require specific queries to be run against the API"
      ;;
    neo4j)
      echo "Neo4j Stats:"
      docker exec neo4j cypher-shell -u neo4j -p "$root_password" "CALL dbms.listConfig() YIELD name, description, value WHERE name CONTAINS 'dbms' RETURN name, value;"
      docker exec neo4j cypher-shell -u neo4j -p "$root_password" "CALL db.stats.retrieve('GRAPH COUNTS');"
      ;;
    redis)
      echo "Redis Stats:"
      docker exec redis redis-cli -a "$root_password" INFO
      ;;
    *)
      echo "Unknown service: $service"
      return 1
      ;;
  esac
}

# View logs for a service
view_logs() {
  local service="$1"
  local container_name
  
  case "$service" in
    postgres) container_name="postgres" ;;
    mariadb) container_name="mariadb" ;;
    mongodb) container_name="mongodb" ;;
    influxdb) container_name="influxdb" ;;
    neo4j) container_name="neo4j" ;;
    redis) container_name="redis" ;;
    *)
      echo "Unknown service: $service"
      return 1
      ;;
  esac
  
  mkdir -p "$LOGS_DIR"
  docker logs $container_name > "$LOGS_DIR/${service}_$(date +%Y%m%d_%H%M%S).log"
  echo "Logs saved to $LOGS_DIR/${service}_$(date +%Y%m%d_%H%M%S).log"
  docker logs --tail=100 $container_name
}

# Execute service operations
execute_operation() {
  local service="$1"
  local cmd="$2"
  
  # Change to Terraform directory
  cd "$TF_DIR" || exit 1
  
  case "$cmd" in
    s)
      echo "Starting $service using Terraform in $TF_DIR..."
      terraform apply -var="root_password=$(load_env && echo $DB_ROOT_PASSWORD || echo $DEFAULT_ROOT_PASSWORD)" -target="docker_container.$service" -auto-approve
      ;;
    k)
      echo "Stopping $service using Terraform in $TF_DIR..."
      terraform destroy -var="root_password=$(load_env && echo $DB_ROOT_PASSWORD || echo $DEFAULT_ROOT_PASSWORD)" -target="docker_container.$service" -auto-approve
      ;;
    r)
      echo "Restarting $service in $TF_DIR..."
      terraform destroy -var="root_password=$(load_env && echo $DB_ROOT_PASSWORD || echo $DEFAULT_ROOT_PASSWORD)" -target="docker_container.$service" -auto-approve
      terraform apply -var="root_password=$(load_env && echo $DB_ROOT_PASSWORD || echo $DEFAULT_ROOT_PASSWORD)" -target="docker_container.$service" -auto-approve
      ;;
    l)
      echo "Fetching $service logs..."
      view_logs "$service"
      ;;
    b)
      echo "Backing up $service..."
      backup_database "$service"
      ;;
    c)
      echo "Connecting to $service CLI..."
      connect_cli "$service"
      ;;
    h)
      echo "Checking $service health..."
      check_health "$service"
      ;;
    t)
      echo "Showing $service stats..."
      show_stats "$service"
      ;;
    *)
      echo "Unknown command $cmd for $service"
      usage
      ;;
  esac
}

# Start all services
start_all() {
  # Change to Terraform directory
  cd "$TF_DIR" || exit 1
  
  echo "Starting all database services with Terraform in $TF_DIR..."
  terraform apply -var="root_password=$(load_env && echo $DB_ROOT_PASSWORD || echo $DEFAULT_ROOT_PASSWORD)" -auto-approve
  echo "✅ All database services started"
}

# Stop all services
stop_all() {
  # Change to Terraform directory
  cd "$TF_DIR" || exit 1
  
  echo "Stopping all database services with Terraform in $TF_DIR..."
  terraform destroy -var="root_password=$(load_env && echo $DB_ROOT_PASSWORD || echo $DEFAULT_ROOT_PASSWORD)" -auto-approve
  echo "✅ All database services stopped"
}

# Show status of all services
show_status() {
  echo "📊 Database Stack Status:"
  echo "-------------------------"
  echo "PostgreSQL: $(docker ps -q -f name=postgres > /dev/null && echo "Running ✅" || echo "Stopped ❌")"
  echo "MariaDB:    $(docker ps -q -f name=mariadb > /dev/null && echo "Running ✅" || echo "Stopped ❌")"
  echo "MongoDB:    $(docker ps -q -f name=mongodb > /dev/null && echo "Running ✅" || echo "Stopped ❌")"
  echo "InfluxDB:   $(docker ps -q -f name=influxdb > /dev/null && echo "Running ✅" || echo "Stopped ❌")"
  echo "Neo4j:      $(docker ps -q -f name=neo4j > /dev/null && echo "Running ✅" || echo "Stopped ❌")"
  echo "Redis:      $(docker ps -q -f name=redis > /dev/null && echo "Running ✅" || echo "Stopped ❌")"
}

# Backup all databases
backup_all() {
  backup_database "postgres"
  backup_database "mariadb"
  backup_database "mongodb"
  backup_database "influxdb"
  backup_database "neo4j"
  backup_database "redis"
  echo "✅ All databases backed up"
}

# Show usage information
usage() {
  echo "Database Stack Control Script (dbctl.sh) - Terraform Version"
  echo "--------------------------------------------------------"
  echo "Usage: dbctl.sh [options]"
  echo ""
  echo "General Options:"
  echo "  -d [directory] Specify the Terraform files directory (default: current directory)"
  echo "  -i [password]  Initialize stack with Terraform (optional root password)"
  echo "  -a [cmd]       All services (s=start, k=stop, t=status, b=backup)"
  echo ""
  echo "Database-specific Options:"
  echo "  -p [cmd]  PostgreSQL commands"
  echo "  -m [cmd]  MariaDB commands"
  echo "  -g [cmd]  MongoDB commands"
  echo "  -f [cmd]  InfluxDB commands"
  echo "  -n [cmd]  Neo4j commands"
  echo "  -r [cmd]  Redis commands"
  echo ""
  echo "Commands for database services:"
  echo "  s         Start the service"
  echo "  k         Stop the service"
  echo "  r         Restart the service"
  echo "  l         View logs"
  echo "  b         Backup database"
  echo "  c         Connect to database CLI"
  echo "  h         Check health status"
  echo "  t         Show database statistics"
  echo ""
  echo "Examples:"
  echo "  ./dbctl.sh -d /path/to/terraform/files -i StrongP@ss"
  echo "  ./dbctl.sh -d terraform_configs -i"
  echo "  ./dbctl.sh -d . -p s"
  echo "  ./dbctl.sh -p s"
  echo "  ./dbctl.sh -m k"
  echo "  ./dbctl.sh -f c"
  echo "  ./dbctl.sh -a s"
  echo "  ./dbctl.sh -a t"
  exit 1
}

# Main execution
if [ "$#" -eq 0 ]; then
  usage
fi

# Process option for directory first
while getopts ":d:" opt; do
  case $opt in
    d) set_tf_dir "$OPTARG" ;;
    *) ;; # Skip other options for now
  esac
done

# Reset OPTIND to process all options again
OPTIND=1

while getopts "d:i:p:m:g:f:n:r:a:" opt; do
  case $opt in
    d) ;; # Already processed
    i) init_stack "$OPTARG" ;;
    p) execute_operation "postgres" "$OPTARG" ;;
    m) execute_operation "mariadb" "$OPTARG" ;;
    g) execute_operation "mongodb" "$OPTARG" ;;
    f) execute_operation "influxdb" "$OPTARG" ;;
    n) execute_operation "neo4j" "$OPTARG" ;;
    r) execute_operation "redis" "$OPTARG" ;;
    a)
      case "$OPTARG" in
        s) start_all ;;
        k) stop_all ;;
        t) show_status ;;
        b) backup_all ;;
        *) echo "Unknown command $OPTARG for all services"; usage ;;
      esac
      ;;
    *) usage ;;
  esac
done