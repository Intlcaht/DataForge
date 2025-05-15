#!/bin/bash

# ==============================================================================
# Database Management Script
# ==============================================================================
#
# This script automates the provisioning, clearing, backing up, restoring, and
# deleting of databases for various database systems including PostgreSQL,
# MariaDB, MongoDB, Neo4j, Redis, and InfluxDB. It reads configuration from a
# YAML file and supports command-line flags for specifying actions and database
# types.
#
# Key Features:
# - Loads configuration from a YAML file using `yq`.
# - Supports provisioning of users and databases for multiple database systems.
# - Provides clear, backup, restore, and delete operations for each database type.
# - Checks for required dependencies before executing commands.
# - Uses command-line flags for ease of use.
# - Includes a help message for usage instructions.
#
# ==========================================
# Usage: ./script.sh [options]
# Defaults: config file = config.yml
# Database identifier format: <db_type>.<db_name>
# ==========================================

# Basic Operations:
# -----------------
# - Provision Databases (from config.yml):
# ./script.sh -p

# # - Clear Data:
# ./script.sh -C -d postgres.main_db

# # - Backup Database:
# ./script.sh -b -d mysql.sales_db backups/sales_backup.sql

# # - Restore Database:
# ./script.sh -r -d postgres.main_db backups/main_db_restore.sql

# # - Delete Database:
# ./script.sh -D -d mongo.analytics_db

# # - Help:
# ./script.sh -h


# # Extended Operations:
# # --------------------
# # - Use Custom Config File:
# ./script.sh -c custom_config.yml -p

# # - Validate Config File:
# ./script.sh --validate

# # - Detect Schema Drift:
# ./script.sh --drift-check -d postgres.main_db

# # - Rotate Secrets:
# ./script.sh --rotate-secrets -d mongo.logs_db

# # - Mask Production Data:
# ./script.sh --mask-data -d mysql.crm_db --target-env staging

# # - Simulate Disaster Recovery:
# ./script.sh --simulate-dr -d postgres.main_db

# # - Generate Schema Documentation:
# ./script.sh --doc-schema -d postgres.main_db --output docs/schema.md

# # - Tag Environment:
# ./script.sh --tag-env --env production

# # - Trigger Monitoring Alert Test:
# ./script.sh --trigger-alert -d mysql.billing_db --scenario high_latency

# # - Sandbox Database for Testing:
# ./script.sh --sandbox -d mongo.test_data --ttl 2h

# # - Enable/Disable RBAC:
# ./script.sh --rbac --enable -d postgres.core_db
# ./script.sh --rbac --disable -d postgres.core_db

# # - Apply Retention Policy:
# ./script.sh --retention-policy --days 30 -d postgres.logs_db

# # - Check Cost Estimates:
# ./script.sh --check-cost -d mysql.prod_db

# # - Test Auth Policy:
# ./script.sh --test-auth-policy -d postgres.secure_db

# # - Lint All Configs (CI/CD safe):
# ./script.sh --lint-all --ci

# # - Plan Schema Changes (Dry Run):
# ./script.sh --plan-schema -d mysql.orders_db

# # - Apply Approved Schema Changes:
# ./script.sh --apply-schema -d mysql.orders_db

#
# Database Types (<db_type>):
# - postgres: PostgreSQL
# - mariadb: MariaDB
# - mongodb: MongoDB
# - neo4j: Neo4j
# - redis: Redis
# - influxdb: InfluxDB
#
# Notes:
# - Ensure `yq` is installed for YAML parsing.
# - Adjust the script as needed for your environment and security practices.
# - Some database operations, like backup and restore for Neo4j, may require
#   additional tools or manual intervention.
#
# ==============================================================================

# Load YAML configuration
load_config() {
    local config_file=$1
    if ! command -v yq &> /dev/null; then
        echo "yq command not found. Please install yq to parse YAML files."
        exit 1
    fi
    eval $(yq eval -o=sh "$config_file")
}

# Check if required dependencies are installed
check_dependencies() {
    local deps=("psql" "mysql" "mongo" "cypher-shell" "redis-cli" "influx" "yq")
    for dep in "${deps[@]}"; do
        if ! command -v $dep &> /dev/null; then
            echo "$dep is not installed. Please install it to proceed."
            exit 1
        fi
    done
}

# Function to provision PostgreSQL databases and users
provision_postgres() {
    local host=$postgres_host
    local port=$postgres_port
    local admin=$postgres_admin
    local admin_password=$postgres_admin_password

    for db in "${!postgres_databases[@]}"; do
        user_info=(${postgres_databases[$db]//:/ })
        user=${user_info[0]}
        password=${user_info[1]}
        permissions=${user_info[2]}

        PGPASSWORD=$admin_password psql -h $host -p $port -U $admin -c "CREATE DATABASE $db;"
        PGPASSWORD=$admin_password psql -h $host -p $port -U $admin -c "CREATE USER $user WITH PASSWORD '$password';"
        PGPASSWORD=$admin_password psql -h $host -p $port -U $admin -c "GRANT $permissions ON DATABASE $db TO $user;"
    done
}

# Function to provision MariaDB databases and users
provision_mariadb() {
    local host=$mariadb_host
    local port=$mariadb_port
    local admin=$mariadb_admin
    local admin_password=$mariadb_admin_password

    for db in "${!mariadb_databases[@]}"; do
        user_info=(${mariadb_databases[$db]//:/ })
        user=${user_info[0]}
        password=${user_info[1]}
        permissions=${user_info[2]}

        mysql -h $host -P $port -u $admin -p$admin_password -e "CREATE DATABASE $db;"
        mysql -h $host -P $port -u $admin -p$admin_password -e "CREATE USER '$user'@'localhost' IDENTIFIED BY '$password';"
        mysql -h $host -P $port -u $admin -p$admin_password -e "GRANT $permissions ON $db.* TO '$user'@'localhost';"
    done
}

# Function to provision MongoDB databases and users
provision_mongodb() {
    local host=$mongodb_host
    local port=$mongodb_port
    local admin=$mongodb_admin
    local admin_password=$mongodb_admin_password

    for db in "${!mongodb_databases[@]}"; do
        user_info=(${mongodb_databases[$db]//:/ })
        user=${user_info[0]}
        password=${user_info[1]}
        roles=${user_info[2]}

        mongo --host $host --port $port -u $admin -p $admin_password --authenticationDatabase admin --eval "
            db = db.getSiblingDB('$db');
            db.createUser({user: '$user', pwd: '$password', roles: [{role: '$roles', db: '$db'}]});
        "
    done
}

# Function to provision Neo4j databases and users
provision_neo4j() {
    local host=$neo4j_host
    local port=$neo4j_port
    local admin=$neo4j_admin
    local admin_password=$neo4j_admin_password

    for db in "${!neo4j_databases[@]}"; do
        user_info=(${neo4j_databases[$db]//:/ })
        user=${user_info[0]}
        password=${user_info[1]}
        roles=${user_info[2]}

        cypher-shell -a $host:$port -u $admin -p $admin_password -d $db "CREATE USER $user SET PASSWORD '$password' SET STATUS ACTIVE;"
        cypher-shell -a $host:$port -u $admin -p $admin_password -d $db "GRANT ROLE $roles TO $user;"
    done
}

# Function to provision Redis databases
provision_redis() {
    local host=$redis_host
    local port=$redis_port
    local admin_password=$redis_admin_password

    for db in "${!redis_databases[@]}"; do
        password=${redis_databases[$db]}
        redis-cli -h $host -p $port -a $admin_password CONFIG SET requirepass $password
    done
}

# Function to provision InfluxDB databases and users
provision_influxdb() {
    local host=$influxdb_host
    local port=$influxdb_port
    local admin_token=$influxdb_admin_token

    for db in "${!influxdb_databases[@]}"; do
        user_info=(${influxdb_databases[$db]//:/ })
        user=${user_info[0]}
        token=${user_info[1]}
        permissions=${user_info[2]}
        bucket=${user_info[3]}
        org=${user_info[4]}

        influx bucket create -n $bucket -o $org --token $admin_token
        influx auth create -d "User for $bucket" -o $org --token $admin_token --user $user --token $token --read-buckets $bucket --write-buckets $bucket
    done
}

# Utility to clear data or drop tables in PostgreSQL
clear_postgres_data() {
    local host=$postgres_host
    local port=$postgres_port
    local admin=$postgres_admin
    local admin_password=$postgres_admin_password
    local db=$1

    PGPASSWORD=$admin_password psql -h $host -p $port -U $admin -d $db -c "DROP SCHEMA public CASCADE; CREATE SCHEMA public;"
}

# Utility to clear data in MariaDB
clear_mariadb_data() {
    local host=$mariadb_host
    local port=$mariadb_port
    local admin=$mariadb_admin
    local admin_password=$mariadb_admin_password
    local db=$1

    mysql -h $host -P $port -u $admin -p$admin_password -e "DROP DATABASE $db; CREATE DATABASE $db;"
}

# Utility to clear data in MongoDB
clear_mongodb_data() {
    local host=$mongodb_host
    local port=$mongodb_port
    local admin=$mongodb_admin
    local admin_password=$mongodb_admin_password
    local db=$1

    mongo --host $host --port $port -u $admin -p $admin_password --authenticationDatabase admin --eval "db.getSiblingDB('$db').dropDatabase();"
}

# Utility to clear data in Neo4j
clear_neo4j_data() {
    local host=$neo4j_host
    local port=$neo4j_port
    local admin=$neo4j_admin
    local admin_password=$neo4j_admin_password
    local db=$1

    cypher-shell -a $host:$port -u $admin -p $admin_password -d $db "MATCH (n) DETACH DELETE n;"
}

# Utility to clear data in Redis
clear_redis_data() {
    local host=$redis_host
    local port=$redis_port
    local admin_password=$redis_admin_password

    redis-cli -h $host -p $port -a $admin_password FLUSHALL
}

# Utility to clear data in InfluxDB
clear_influxdb_data() {
    local host=$influxdb_host
    local port=$influxdb_port
    local admin_token=$influxdb_admin_token
    local bucket=$1
    local org=$2

    influx delete --bucket $bucket --org $org --token $admin_token --start 1970-01-01 --stop $(date +%Y-%m-%d)
}

# Utility to backup PostgreSQL database
backup_postgres() {
    local host=$postgres_host
    local port=$postgres_port
    local admin=$postgres_admin
    local admin_password=$postgres_admin_password
    local db=$1
    local backup_file=$2

    PGPASSWORD=$admin_password pg_dump -h $host -p $port -U $admin -d $db -F c -b -v -f $backup_file
}

# Utility to backup MariaDB database
backup_mariadb() {
    local host=$mariadb_host
    local port=$mariadb_port
    local admin=$mariadb_admin
    local admin_password=$mariadb_admin_password
    local db=$1
    local backup_file=$2

    mysqldump -h $host -P $port -u $admin -p$admin_password $db > $backup_file
}

# Utility to backup MongoDB database
backup_mongodb() {
    local host=$mongodb_host
    local port=$mongodb_port
    local admin=$mongodb_admin
    local admin_password=$mongodb_admin_password
    local db=$1
    local backup_file=$2

    mongodump --host $host --port $port -u $admin -p $admin_password --authenticationDatabase admin --db $db --archive=$backup_file
}

# Utility to backup Neo4j database
backup_neo4j() {
    local host=$neo4j_host
    local port=$neo4j_port
    local admin=$neo4j_admin
    local admin_password=$neo4j_admin_password
    local db=$1
    local backup_file=$2

    echo "Backup for Neo4j is not directly supported via command line. Please use Neo4j's backup tools."
}

# Utility to backup Redis database
backup_redis() {
    local host=$redis_host
    local port=$redis_port
    local admin_password=$redis_admin_password
    local backup_file=$1

    redis-cli -h $host -p $port -a $admin_password SAVE | cp /var/lib/redis/dump.rdb $backup_file
}

# Utility to backup InfluxDB database
backup_influxdb() {
    local host=$influxdb_host
    local port=$influxdb_port
    local admin_token=$influxdb_admin_token
    local bucket=$1
    local backup_file=$2

    influxd backup $backup_file --bucket $bucket --token $admin_token
}

# Utility to restore PostgreSQL database
restore_postgres() {
    local host=$postgres_host
    local port=$postgres_port
    local admin=$postgres_admin
    local admin_password=$postgres_admin_password
    local db=$1
    local backup_file=$2

    PGPASSWORD=$admin_password pg_restore -h $host -p $port -U $admin -d $db -v $backup_file
}

# Utility to restore MariaDB database
restore_mariadb() {
    local host=$mariadb_host
    local port=$mariadb_port
    local admin=$mariadb_admin
    local admin_password=$mariadb_admin_password
    local db=$1
    local backup_file=$2

    mysql -h $host -P $port -u $admin -p$admin_password $db < $backup_file
}

# Utility to restore MongoDB database
restore_mongodb() {
    local host=$mongodb_host
    local port=$mongodb_port
    local admin=$mongodb_admin
    local admin_password=$mongodb_admin_password
    local db=$1
    local backup_file=$2

    mongorestore --host $host --port $port -u $admin -p $admin_password --authenticationDatabase admin --db $db --archive=$backup_file
}

# Utility to restore Neo4j database
restore_neo4j() {
    local host=$neo4j_host
    local port=$neo4j_port
    local admin=$neo4j_admin
    local admin_password=$neo4j_admin_password
    local db=$1
    local backup_file=$2

    echo "Restore for Neo4j is not directly supported via command line. Please use Neo4j's restore tools."
}

# Utility to restore Redis database
restore_redis() {
    local host=$redis_host
    local port=$redis_port
    local admin_password=$redis_admin_password
    local backup_file=$1

    cp $backup_file /var/lib/redis/dump.rdb
    redis-cli -h $host -p $port -a $admin_password CONFIG SET dir /var/lib/redis
    redis-cli -h $host -p $port -a $admin_password CONFIG SET dbfilename dump.rdb
}

# Utility to restore InfluxDB database
restore_influxdb() {
    local host=$influxdb_host
    local port=$influxdb_port
    local admin_token=$influxdb_admin_token
    local bucket=$1
    local backup_file=$2

    influxd restore $backup_file --bucket $bucket --token $admin_token
}

# Utility to delete PostgreSQL database
delete_postgres_db() {
    local host=$postgres_host
    local port=$postgres_port
    local admin=$postgres_admin
    local admin_password=$postgres_admin_password
    local db=$1

    PGPASSWORD=$admin_password psql -h $host -p $port -U $admin -c "DROP DATABASE $db;"
}

# Utility to delete MariaDB database
delete_mariadb_db() {
    local host=$mariadb_host
    local port=$mariadb_port
    local admin=$mariadb_admin
    local admin_password=$mariadb_admin_password
    local db=$1

    mysql -h $host -P $port -u $admin -p$admin_password -e "DROP DATABASE $db;"
}

# Utility to delete MongoDB database
delete_mongodb_db() {
    local host=$mongodb_host
    local port=$mongodb_port
    local admin=$mongodb_admin
    local admin_password=$mongodb_admin_password
    local db=$1

    mongo --host $host --port $port -u $admin -p $admin_password --authenticationDatabase admin --eval "db.getSiblingDB('$db').dropDatabase();"
}

# Utility to delete Neo4j database
delete_neo4j_db() {
    local host=$neo4j_host
    local port=$neo4j_port
    local admin=$neo4j_admin
    local admin_password=$neo4j_admin_password
    local db=$1

    cypher-shell -a $host:$port -u $admin -p $admin_password -d $db "DROP DATABASE $db;"
}

# Utility to delete Redis database
delete_redis_db() {
    local host=$redis_host
    local port=$redis_port
    local admin_password=$redis_admin_password

    redis-cli -h $host -p $port -a $admin_password FLUSHALL
}

# Utility to delete InfluxDB database
delete_influxdb_db() {
    local host=$influxdb_host
    local port=$influxdb_port
    local admin_token=$influxdb_admin_token
    local bucket=$1
    local org=$2

    influx bucket delete --bucket $bucket --org $org --token $admin_token
}

# Help message
show_help() {
    echo "Usage: $0 [options]"
    echo "Options:"
    echo "  -c, --config     Path to the YAML configuration file."
    echo "  -p, --provision  Provision databases and users."
    echo "  -C, --clear      Clear data in a database. Requires -t and -n."
    echo "  -b, --backup     Backup a database. Requires -t and -n."
    echo "  -r, --restore    Restore a database. Requires -t and -n."
    echo "  -d, --delete     Delete a database. Requires -t and -n."
    echo "  -t, --type       Database type (postgres, mariadb, mongodb, neo4j, redis, influxdb)."
    echo "  -n, --name       Database name."
    echo "  -h, --help       Show this help message."
}

# Main script execution
main() {
    local config_file=""
    local action=""
    local db_type=""
    local db_name=""
    local backup_file=""

    while [[ $# -gt 0 ]]; do
        case $1 in
            -c|--config)
                config_file="$2"
                shift 2
                ;;
            -p|--provision)
                action="provision"
                shift
                ;;
            -C|--clear)
                action="clear"
                shift
                ;;
            -b|--backup)
                action="backup"
                backup_file="$3"
                shift 2
                ;;
            -r|--restore)
                action="restore"
                backup_file="$3"
                shift 2
                ;;
            -d|--delete)
                action="delete"
                shift
                ;;
            -t|--type)
                db_type="$2"
                shift 2
                ;;
            -n|--name)
                db_name="$2"
                shift 2
                ;;
            -h|--help)
                show_help
                exit 0
                ;;
            *)
                echo "Unknown option: $1"
                show_help
                exit 1
                ;;
        esac
    done

    if [ -z "$config_file" ]; then
        echo "Configuration file is required."
        show_help
        exit 1
    fi

    load_config "$config_file"
    check_dependencies

    case $action in
        provision)
            provision_postgres
            provision_mariadb
            provision_mongodb
            provision_neo4j
            provision_redis
            provision_influxdb
            ;;
        clear)
            case $db_type in
                postgres)
                    clear_postgres_data "$db_name"
                    ;;
                mariadb)
                    clear_mariadb_data "$db_name"
                    ;;
                mongodb)
                    clear_mongodb_data "$db_name"
                    ;;
                neo4j)
                    clear_neo4j_data "$db_name"
                    ;;
                redis)
                    clear_redis_data
                    ;;
                influxdb)
                    clear_influxdb_data "$db_name" "$org"
                    ;;
                *)
                    echo "Unsupported database type for clear action."
                    exit 1
                    ;;
            esac
            ;;
        backup)
            case $db_type in
                postgres)
                    backup_postgres "$db_name" "$backup_file"
                    ;;
                mariadb)
                    backup_mariadb "$db_name" "$backup_file"
                    ;;
                mongodb)
                    backup_mongodb "$db_name" "$backup_file"
                    ;;
                neo4j)
                    backup_neo4j "$db_name" "$backup_file"
                    ;;
                redis)
                    backup_redis "$backup_file"
                    ;;
                influxdb)
                    backup_influxdb "$db_name" "$backup_file"
                    ;;
                *)
                    echo "Unsupported database type for backup action."
                    exit 1
                    ;;
            esac
            ;;
        restore)
            case $db_type in
                postgres)
                    restore_postgres "$db_name" "$backup_file"
                    ;;
                mariadb)
                    restore_mariadb "$db_name" "$backup_file"
                    ;;
                mongodb)
                    restore_mongodb "$db_name" "$backup_file"
                    ;;
                neo4j)
                    restore_neo4j "$db_name" "$backup_file"
                    ;;
                redis)
                    restore_redis "$backup_file"
                    ;;
                influxdb)
                    restore_influxdb "$db_name" "$backup_file"
                    ;;
                *)
                    echo "Unsupported database type for restore action."
                    exit 1
                    ;;
            esac
            ;;
        delete)
            case $db_type in
                postgres)
                    delete_postgres_db "$db_name"
                    ;;
                mariadb)
                    delete_mariadb_db "$db_name"
                    ;;
                mongodb)
                    delete_mongodb_db "$db_name"
                    ;;
                neo4j)
                    delete_neo4j_db "$db_name"
                    ;;
                redis)
                    delete_redis_db
                    ;;
                influxdb)
                    delete_influxdb_db "$db_name" "$org"
                    ;;
                *)
                    echo "Unsupported database type for delete action."
                    exit 1
                    ;;
            esac
            ;;
        *)
            echo "No action specified."
            show_help
            exit 1
            ;;
    esac
}

main "$@"
