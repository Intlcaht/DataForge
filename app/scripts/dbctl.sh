TODO use terraform support
#!/bin/bash
###########################################################
# dbctl.sh - Database Stack Control Script
#
# A utility script to manage development database environments using Docker.
# Supports PostgreSQL, MariaDB, MongoDB, InfluxDB, Neo4j, and Redis with standardized controls.
#
# Usage: dbctl.sh [options]"

# GENERAL COMMANDS:
#   -i [password]    Initialize the entire database stack with optional root password
#   -a [cmd]         Execute command on all services (see SERVICE COMMANDS below)
#
# SERVICE-SPECIFIC COMMANDS (use with -p, -m, -g, -f, -n, or -r):
#   s                Start the service
#   k                Stop the service
#   r                Restart the service
#   l                View service logs (saves to logs/ directory)
#   b                Backup the database (saves to backups/ directory)
#   c                Connect to database CLI
#   h                Check service health status
#   t                Show database statistics
#
# SERVICE SELECTORS:
#   -p               Target PostgreSQL service
#   -m               Target MariaDB service
#   -g               Target MongoDB service
#   -f               Target InfluxDB service
#   -n               Target Neo4j service
#   -r               Target Redis service
#
# COMPLETE EXAMPLES:
# 
# INITIALIZATION:
#   ./dbctl.sh -i                # Initialize with default password
#   ./dbctl.sh -i StrongPass123  # Initialize with custom password
#
# POSTGRESQL EXAMPLES:
#   ./dbctl.sh -p s              # Start PostgreSQL
#   ./dbctl.sh -p k              # Stop PostgreSQL
#   ./dbctl.sh -p r              # Restart PostgreSQL
#   ./dbctl.sh -p l              # View PostgreSQL logs
#   ./dbctl.sh -p b              # Backup PostgreSQL
#   ./dbctl.sh -p c              # Connect to PostgreSQL CLI
#   ./dbctl.sh -p h              # Check PostgreSQL health
#   ./dbctl.sh -p t              # Show PostgreSQL stats
#
# MARIADB EXAMPLES:
#   ./dbctl.sh -m s              # Start MariaDB
#   ./dbctl.sh -m k              # Stop MariaDB
#   ./dbctl.sh -m r              # Restart MariaDB
#   ./dbctl.sh -m l              # View MariaDB logs
#   ./dbctl.sh -m b              # Backup MariaDB
#   ./dbctl.sh -m c              # Connect to MariaDB CLI
#   ./dbctl.sh -m h              # Check MariaDB health
#   ./dbctl.sh -m t              # Show MariaDB stats
#
# MONGODB EXAMPLES:
#   ./dbctl.sh -g s              # Start MongoDB
#   ./dbctl.sh -g k              # Stop MongoDB
#   ./dbctl.sh -g r              # Restart MongoDB
#   ./dbctl.sh -g l              # View MongoDB logs
#   ./dbctl.sh -g b              # Backup MongoDB
#   ./dbctl.sh -g c              # Connect to MongoDB CLI
#   ./dbctl.sh -g h              # Check MongoDB health
#   ./dbctl.sh -g t              # Show MongoDB stats
#
# INFLUXDB EXAMPLES:
#   ./dbctl.sh -f s              # Start InfluxDB
#   ./dbctl.sh -f k              # Stop InfluxDB
#   ./dbctl.sh -f r              # Restart InfluxDB
#   ./dbctl.sh -f l              # View InfluxDB logs
#   ./dbctl.sh -f b              # Backup InfluxDB
#   ./dbctl.sh -f c              # Connect to InfluxDB CLI
#   ./dbctl.sh -f h              # Check InfluxDB health
#   ./dbctl.sh -f t              # Show InfluxDB stats
#
# NEO4J EXAMPLES:
#   ./dbctl.sh -n s              # Start Neo4j
#   ./dbctl.sh -n k              # Stop Neo4j
#   ./dbctl.sh -n r              # Restart Neo4j
#   ./dbctl.sh -n l              # View Neo4j logs
#   ./dbctl.sh -n b              # Backup Neo4j
#   ./dbctl.sh -n c              # Connect to Neo4j CLI
#   ./dbctl.sh -n h              # Check Neo4j health
#   ./dbctl.sh -n t              # Show Neo4j stats
#
# REDIS EXAMPLES:
#   ./dbctl.sh -r s              # Start Redis
#   ./dbctl.sh -r k              # Stop Redis
#   ./dbctl.sh -r r              # Restart Redis
#   ./dbctl.sh -r l              # View Redis logs
#   ./dbctl.sh -r b              # Backup Redis
#   ./dbctl.sh -r c              # Connect to Redis CLI
#   ./dbctl.sh -r h              # Check Redis health
#   ./dbctl.sh -r t              # Show Redis stats
#
# ALL SERVICES EXAMPLES:
#   ./dbctl.sh -a s              # Start all services
#   ./dbctl.sh -a k              # Stop all services
#   ./dbctl.sh -a r              # Restart all services
#   ./dbctl.sh -a l              # View all logs
#   ./dbctl.sh -a b              # Backup all databases
#   ./dbctl.sh -a h              # Check all services health
#   ./dbctl.sh -a t              # Show all services stats
##############################################################

# Examples:"
#   ./dbctl.sh -i                # Initialize the stack"
#   ./dbctl.sh -p s              # Start PostgreSQL"
#   ./dbctl.sh -m k              # Stop MariaDB"
#   ./dbctl.sh -g l              # View MongoDB logs"
#   ./dbctl.sh -p c              # Connect to PostgreSQL CLI"
#   ./dbctl.sh -a s              # Start all services"
#   ./dbctl.sh -a t              # Show status of all services"
#   ./dbctl.sh -p b              # Backup PostgreSQL"
#
# Author: Database DevOps Team
# Version: 1.1.0
# Last Updated: 2025-04-08
##############################################################################

# Project root directory
ROOT_DIR="$(pwd)/dbstack"
mkdir -p "$ROOT_DIR"
cd "$ROOT_DIR" || exit 1

# Configuration files
POSTGRES_YML="postgres-compose.yml"
MARIADB_YML="mariadb-compose.yml"
MONGODB_YML="mongodb-compose.yml"
INFLUXDB_YML="influxdb-compose.yml"
NEO4J_YML="neo4j-compose.yml"
REDIS_YML="redis-compose.yml"
CONFIG_DIR="config"
SECRETS_DIR="secrets"

# Logs directory
LOGS_DIR="logs"

# Default password (will be overridden if provided via argument)
DEFAULT_ROOT_PASSWORD="password"

##############################################################################
# Project Structure:
# dbstack/
# ├── data/
# │   ├── postgres/
# │   ├── mariadb/
# │   ├── mongodb/
# │   ├── mongodb-log/
# │   ├── influxdb/
# │   ├── neo4j/
# │   └── redis/
# ├── config/
# │   ├── postgres/
# │   ├── mariadb/
# │   ├── mongodb/
# │   ├── influxdb/
# │   ├── neo4j/
# │   └── redis/
# ├── secrets/
# │   ├── influxdb2-admin-username
# │   ├── influxdb2-admin-password
# │   ├── influxdb2-admin-token
# │   └── neo4j_auth.txt
# ├── logs/
# ├── mongodb/
# │   └── initdb.d/mongo-init.js
# ├── postgres-compose.yml
# ├── mariadb-compose.yml
# ├── mongodb-compose.yml
# ├── influxdb-compose.yml
# ├── neo4j-compose.yml
# ├── redis-compose.yml
# └── dbctl.sh
##############################################################################

# Helper to write compose files
write_compose_files() {
  local root_password="$1"
  
  # Create config directories
  mkdir -p "$CONFIG_DIR/postgres" "$CONFIG_DIR/mariadb" "$CONFIG_DIR/mongodb" "$CONFIG_DIR/influxdb" "$CONFIG_DIR/neo4j" "$CONFIG_DIR/redis" "$LOGS_DIR"
  mkdir -p "$SECRETS_DIR"
  # PostgreSQL
  cat > "$POSTGRES_YML" <<EOF
version: '3.8'
services:
  postgres:
    image: postgres:latest
    container_name: postgres
    restart: unless-stopped
    environment:
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=${root_password}
    volumes:
      - postgres-data:/var/lib/postgresql/data
      - ./config/postgres:/etc/postgresql/conf.d
    ports:
      - 5432:5432
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 10s
      timeout: 5s
      retries: 5
  volumes:
    postgres-data:
EOF

  # MariaDB
  cat > "$MARIADB_YML" <<EOF
version: '3'
services:
  mariadb:
    image: mariadb:10.5
    command: --transaction-isolation=READ-COMMITTED --binlog-format=ROW
    container_name: mariadb
    restart: unless-stopped
    volumes:
      - .mariadb-data:/var/lib/mysql:rw
      - ./config/mariadb:/etc/mysql/conf.d
    ports:
      - "3307:3306"
    environment:
      - MYSQL_ROOT_PASSWORD=${root_password}
      - MYSQL_DATABASE=appwrite
      - MYSQL_USER=user
      - MYSQL_PASSWORD=${root_password}
    command: 'mysqld --innodb-flush-method=fsync'
    healthcheck:
      test: ["CMD", "mysqladmin", "ping", "-h", "localhost", "-u", "root", "-p${root_password}"]
      interval: 10s
      timeout: 5s
      retries: 5
  volumes:
    mariadb-data:
EOF

  # MongoDB
  mkdir -p ./mongodb/initdb.d
  cat > ./mongodb/initdb.d/mongo-init.js <<EOF
// MongoDB initialization script
db.createUser({
  user: 'appuser',
  pwd: '${root_password}',
  roles: [{ role: 'readWrite', db: 'application' }]
});
EOF

  cat > "$MONGODB_YML" <<EOF
version: '3.9'
services:
  mongodb:
    image: mongo:latest
    container_name: mongodb
    hostname: mongodb
    restart: unless-stopped
    volumes:
      - ./mongodb/initdb.d/mongo-init.js:/docker-entrypoint-initdb.d/mongo-init.js:ro
      - mongodb-data:/data/db/
      - ./data/mongodb-log:/var/log/mongodb/
      - ./config/mongodb:/etc/mongo
    environment:
      MONGO_INITDB_ROOT_USERNAME: root
      MONGO_INITDB_ROOT_PASSWORD: ${root_password}
    ports:
      - "27017:27017"
    healthcheck:
      test: echo 'db.runCommand("ping").ok' | mongosh mongodb:27017/test --quiet
      interval: 10s
      timeout: 5s
      retries: 5
  volumes:
    mongodb-data:
EOF

  # InfluxDB2
  mkdir -p ./data/influxdb
  
  # Create secret files
  echo "admin" > "$SECRETS_DIR/influxdb2-admin-username"
  echo "${root_password}" > "$SECRETS_DIR/influxdb2-admin-password"
  
  # Generate a random token for InfluxDB
  local influx_token
  influx_token=$(openssl rand -hex 32)
  echo "${influx_token}" > "$SECRETS_DIR/influxdb2-admin-token"
  
  cat > "$INFLUXDB_YML" <<EOF
version: '3.9'
services:
  influxdb2:
    image: influxdb:2
    container_name: influxdb
    restart: unless-stopped
    ports:
      - "8086:8086"
    environment:
      DOCKER_INFLUXDB_INIT_MODE: setup
      DOCKER_INFLUXDB_INIT_USERNAME_FILE: /run/secrets/influxdb2-admin-username
      DOCKER_INFLUXDB_INIT_PASSWORD_FILE: /run/secrets/influxdb2-admin-password
      DOCKER_INFLUXDB_INIT_ADMIN_TOKEN_FILE: /run/secrets/influxdb2-admin-token
      DOCKER_INFLUXDB_INIT_ORG: itlc
      DOCKER_INFLUXDB_INIT_BUCKET: b0
    volumes:
      - influxdb2-data:/var/lib/influxdb2
      - ./config/influxdb:/etc/influxdb2
    secrets:
      - influxdb2-admin-username
      - influxdb2-admin-password
      - influxdb2-admin-token
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8086/health"]
      interval: 30s
      timeout: 10s
      retries: 5
      
secrets:
  influxdb2-admin-username:
    file: ./secrets/influxdb2-admin-username
  influxdb2-admin-password:
    file: ./secrets/influxdb2-admin-password
  influxdb2-admin-token:
    file: ./secrets/influxdb2-admin-token
      
volumes:
  influxdb2-data:
  influxdb2-config:
EOF

  # Neo4j
  mkdir -p ./data/neo4j/{logs,data,plugins,config}
  echo "neo4j/${root_password}" > "$SECRETS_DIR/neo4j_auth.txt"
  
  cat > "$NEO4J_YML" <<EOF
version: '3.8'
services:
  neo4j:
    image: neo4j:latest
    container_name: neo4j
    volumes:
      - ./data/neo4j/logs:/logs
      - ./data/neo4j/data:/data
      - ./data/neo4j/plugins:/plugins
      - ./config/neo4j:/config
    environment:
      - NEO4J_AUTH_FILE=/run/secrets/neo4j_auth_file
    ports:
      - "7474:7474"
      - "7687:7687"
    restart: always
    secrets:
      - neo4j_auth_file
    healthcheck:
      test: ["CMD", "cypher-shell", "-u", "neo4j", "-p", "${root_password}", "RETURN 1"]
      interval: 30s
      timeout: 10s
      retries: 5

secrets:
  neo4j_auth_file:
    file: ./secrets/neo4j_auth.txt
EOF

  # Redis
  mkdir -p ./data/redis
  
  cat > "$REDIS_YML" <<EOF
version: '3.8'
services:
  redis:
    image: redis:6.2-alpine
    container_name: redis
    restart: always
    ports:
      - '6379:6379'
    command: redis-server --save 20 1 --loglevel warning --requirepass ${root_password}
    volumes:
      - ./data/redis:/data
      - ./config/redis:/usr/local/etc/redis
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5
EOF

  # Create a .env file to store credentials for later use
  cat > .env <<EOF
DB_ROOT_PASSWORD=${root_password}
INFLUXDB_TOKEN=${influx_token}
EOF
  chmod 600 .env
  chmod 600 "$SECRETS_DIR"/*
  
  echo "✅ Compose files created with custom root password"
}

# Scan for external volumes/networks and create them
scan_and_create_externals() {
  echo "🔍 Scanning for external networks and volumes..."
  for file in *.yml; do
    [ -f "$file" ] || continue
    # Volumes
    grep -E 'external: true' "$file" | sed -n '/volumes:/,/[^[:space:]]/p' | grep -oP '^\s{2,}(\w+):' | awk '{print $1}' | while read -r vol; do
      echo "📦 Creating volume: $vol"
      docker volume create "$vol"
    done
    # Networks
    grep -E 'external: true' "$file" | sed -n '/networks:/,/[^[:space:]]/p' | grep -oP '^\s{2,}(\w+):' | awk '{print $1}' | while read -r net; do
      echo "🌐 Creating network: $net"
      docker network create "$net"
    done
  done
}

# Initialize directory structure
init_stack() {
  local root_password="${1:-$DEFAULT_ROOT_PASSWORD}"
  
  # Check if the password is provided and meets minimum requirements
  if [ "$root_password" == "$DEFAULT_ROOT_PASSWORD" ]; then
    echo "⚠️ Warning: Using default password. For production environments, provide a strong password."
  elif [ ${#root_password} -lt 8 ]; then
    echo "⚠️ Warning: Password is less than 8 characters. Consider using a stronger password."
  fi
  
  mkdir -p ./data/{postgres,mariadb,mongodb,mongodb-log,influxdb,neo4j,redis}
  mkdir -p ./config/{postgres,mariadb,mongodb,influxdb,neo4j,redis}
  mkdir -p "$LOGS_DIR" "$SECRETS_DIR"
  
  write_compose_files "$root_password"
  scan_and_create_externals
  echo "✅ Stack initialized in $ROOT_DIR with custom root password"
}

# Load environment variables if .env exists
load_env() {
  if [ -f .env ]; then
    export $(grep -v '^#' .env | xargs)
  fi
}

# Backup database
backup_database() {
  local service="$1"
  local timestamp=$(date +"%Y%m%d_%H%M%S")
  local backup_dir="$ROOT_DIR/backups/$service"
  
  # Load environment variables for password
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
      
      # Create a backup using the influx CLI
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

# Check database health
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
  
  # Load environment variables for password
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

# Display database stats
show_stats() {
  local service="$1"
  
  # Load environment variables for password
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

# View logs
view_logs() {
  local service="$1"
  local file
  
  case "$service" in
    postgres) file="$POSTGRES_YML" ;;
    mariadb) file="$MARIADB_YML" ;;
    mongodb) file="$MONGODB_YML" ;;
    influxdb) file="$INFLUXDB_YML" ;;
    neo4j) file="$NEO4J_YML" ;;
    redis) file="$REDIS_YML" ;;
    *)
      echo "Unknown service: $service"
      return 1
      ;;
  esac
  
  mkdir -p "$LOGS_DIR"
  docker-compose -f "$file" logs > "$LOGS_DIR/${service}_$(date +%Y%m%d_%H%M%S).log"
  echo "Logs saved to $LOGS_DIR/${service}_$(date +%Y%m%d_%H%M%S).log"
  
  # Also show logs in terminal
  docker-compose -f "$file" logs --tail=100
}

# Command executor
execute_compose() {
  local service="$1"
  local cmd="$2"
  local file="$3"
  
  case "$cmd" in
    s) 
      echo "Starting $service..."
      docker-compose -f "$file" up -d 
      ;;
    k) 
      echo "Stopping $service..."
      docker-compose -f "$file" down 
      ;;
    r) 
      echo "Restarting $service..."
      docker-compose -f "$file" restart 
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
  docker-compose -f "$POSTGRES_YML" -f "$MARIADB_YML" -f "$MONGODB_YML" -f "$INFLUXDB_YML" -f "$NEO4J_YML" -f "$REDIS_YML" up -d
  echo "✅ All database services started"
}

# Stop all services
stop_all() {
  docker-compose -f "$POSTGRES_YML" -f "$MARIADB_YML" -f "$MONGODB_YML" -f "$INFLUXDB_YML" -f "$NEO4J_YML" -f "$REDIS_YML" down
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

# Usage info
usage() {
  echo "Database Stack Control Script (dbctl.sh)"
  echo "---------------------------------------"
  echo "Usage: dbctl.sh [options]"
  echo ""
  echo "General Options:"
  echo "  -i [password]  Initialize stack and volumes with optional root password"
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
  echo "  ./dbctl.sh -i StrongP@ss        # Initialize with custom password"
  echo "  ./dbctl.sh -i                   # Initialize with default password"
  echo "  ./dbctl.sh -p s                 # Start PostgreSQL"
  echo "  ./dbctl.sh -m k                 # Stop MariaDB"
  echo "  ./dbctl.sh -f c                 # Connect to InfluxDB CLI"
  echo "  ./dbctl.sh -g l                 # View MongoDB logs"
  echo "  ./dbctl.sh -n s                 # Start Neo4j"
  echo "  ./dbctl.sh -r c                 # Connect to Redis CLI"
  echo "  ./dbctl.sh -a s                 # Start all services"
  echo "  ./dbctl.sh -a t                 # Show status of all services"
  echo "  ./dbctl.sh -f b                 # Backup InfluxDB"
  exit 1
}

# Main CLI parser
if [ "$#" -eq 0 ]; then
  usage
fi

while getopts "i:p:m:g:f:n:r:a:" opt; do
  case $opt in
    i) init_stack "$OPTARG" ;;
    p) execute_compose "postgres" "$OPTARG" "$POSTGRES_YML" ;;
    m) execute_compose "mariadb" "$OPTARG" "$MARIADB_YML" ;;
    g) execute_compose "mongodb" "$OPTARG" "$MONGODB_YML" ;;
    f) execute_compose "influxdb" "$OPTARG" "$INFLUXDB_YML" ;;
    n) execute_compose "neo4j" "$OPTARG" "$NEO4J_YML" ;;
    r) execute_compose "redis" "$OPTARG" "$REDIS_YML" ;;
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