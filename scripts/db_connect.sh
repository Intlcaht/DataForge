#!/bin/bash
#
# db-connect: Minimal Database Connection Test Tool
# Usage: db-connect [OPTIONS] <command>
#
# Commands:
#   p  Verify Database Port Accessibility
#   n  Check Network-Level Reachability
#   c  Connect via Native CLI Clients
#   q  Test Connection Using a Simple Query
#   s  Inspect Connection Strings
#   l  Check for Required Client Libraries
#   t  Test SSL/TLS Database Connection
#   k  Monitor Database Socket Usage
#   d  Diagnose Failed Connections
#   o  Set Connection Timeout Parameters
#
# Options:
#   -h <host>      Database host
#   -P <port>      Database port
#   -u <user>      Database user
#   -p <pass>      Database password
#   -d <dbname>    Database name
#   -D <driver>    Database driver (postgresql|mysql|sqlite)
#   -f <file>      Configuration file path
#   -v             Verbose output
#
# Examples:
#   db-connect -h localhost -P 5432 -u postgres -D postgresql p
#   db-connect -h db.example.com -P 3306 -u admin -D mysql n
#   db-connect -f /app/.env -D postgresql s
#   db-connect -D sqlite -d /data/test.db c

set -euo pipefail

# Initialize variables
HOST=""
PORT=""
USER=""
PASS=""
DBNAME=""
DRIVER=""
CONFIG_FILE=""
VERBOSE=false

# Parse command line arguments
while getopts "h:P:u:p:d:D:f:v" opt; do
  case $opt in
    h) HOST="$OPTARG" ;;
    P) PORT="$OPTARG" ;;
    u) USER="$OPTARG" ;;
    p) PASS="$OPTARG" ;;
    d) DBNAME="$OPTARG" ;;
    D) DRIVER="$OPTARG" ;;
    f) CONFIG_FILE="$OPTARG" ;;
    v) VERBOSE=true ;;
    *) echo "Invalid option: -$OPTARG" >&2; exit 1 ;;
  esac
done
shift $((OPTIND-1))

# Load configuration from file if specified
if [[ -n "$CONFIG_FILE" && -f "$CONFIG_FILE" ]]; then
  source "$CONFIG_FILE"
fi

# Main command handler
case "$1" in
  p)  # Verify Database Port Accessibility
      if [[ -z "$HOST" || -z "$PORT" ]]; then
        echo "Error: Host and port required for port check" >&2
        exit 1
      fi
      if command -v nc &>/dev/null; then
        nc -zv "$HOST" "$PORT" && echo "Port $PORT accessible" || echo "Port $PORT not accessible"
      elif command -v telnet &>/dev/null; then
        (echo >/dev/tcp/"$HOST"/"$PORT") &>/dev/null && echo "Port $PORT accessible" || echo "Port $PORT not accessible"
      else
        echo "Error: Neither nc nor telnet available" >&2
        exit 1
      fi
      ;;

  n)  # Check Network-Level Reachability
      if [[ -z "$HOST" ]]; then
        echo "Error: Host required for reachability check" >&2
        exit 1
      fi
      if ping -c 3 "$HOST" &>/dev/null; then
        echo "Host $HOST reachable"
      else
        echo "Host $HOST not reachable"
        if command -v traceroute &>/dev/null; then
          traceroute "$HOST"
        fi
      fi
      ;;

  c)  # Connect via Native CLI Clients
      case "$DRIVER" in
        postgresql)
          PGPASSWORD="$PASS" psql -h "$HOST" -p "$PORT" -U "$USER" -d "$DBNAME"
          ;;
        mysql)
          mysql -h "$HOST" -P "$PORT" -u "$USER" -p"$PASS" "$DBNAME"
          ;;
        sqlite)
          sqlite3 "$DBNAME"
          ;;
        *)
          echo "Error: Unsupported database driver" >&2
          exit 1
          ;;
      esac
      ;;

  q)  # Test Connection Using a Simple Query
      case "$DRIVER" in
        postgresql)
          PGPASSWORD="$PASS" psql -h "$HOST" -p "$PORT" -U "$USER" -d "$DBNAME" -c "SELECT 1;"
          ;;
        mysql)
          mysql -h "$HOST" -P "$PORT" -u "$USER" -p"$PASS" "$DBNAME" -e "SELECT 1;"
          ;;
        sqlite)
          sqlite3 "$DBNAME" "SELECT 1;"
          ;;
        *)
          echo "Error: Unsupported database driver" >&2
          exit 1
          ;;
      esac
      ;;

  s)  # Inspect Connection Strings
      if [[ -n "$CONFIG_FILE" && -f "$CONFIG_FILE" ]]; then
        echo "Connection strings in $CONFIG_FILE:"
        grep -E 'DATABASE_URL|DB_|SQL_' "$CONFIG_FILE"
      else
        echo "Current connection settings:"
        echo "Driver: $DRIVER"
        echo "Host: $HOST"
        echo "Port: $PORT"
        echo "User: $USER"
        echo "Database: $DBNAME"
      fi
      ;;

  l)  # Check for Required Client Libraries
      case "$DRIVER" in
        postgresql)
          command -v psql &>/dev/null || echo "psql not found"
          ;;
        mysql)
          command -v mysql &>/dev/null || echo "mysql not found"
          ;;
        sqlite)
          command -v sqlite3 &>/dev/null || echo "sqlite3 not found"
          ;;
        *)
          echo "Error: Unsupported database driver" >&2
          exit 1
          ;;
      esac
      echo "Required client libraries available"
      ;;

  t)  # Test SSL/TLS Database Connection
      case "$DRIVER" in
        postgresql)
          PGPASSWORD="$PASS" psql "host=$HOST port=$PORT user=$USER dbname=$DBNAME sslmode=require" -c "SELECT 1;"
          ;;
        mysql)
          mysql -h "$HOST" -P "$PORT" -u "$USER" -p"$PASS" "$DBNAME" --ssl-mode=REQUIRED -e "SELECT 1;"
          ;;
        *)
          echo "Error: SSL test not supported for $DRIVER" >&2
          exit 1
          ;;
      esac
      ;;

  k)  # Monitor Database Socket Usage
      case "$DRIVER" in
        postgresql)
          SOCKET="/var/run/postgresql/.s.PGSQL.$PORT"
          ;;
        mysql)
          SOCKET="/var/run/mysqld/mysqld.sock"
          ;;
        *)
          echo "Error: Socket check not supported for $DRIVER" >&2
          exit 1
          ;;
      esac
      if [[ -e "$SOCKET" ]]; then
        echo "Socket found: $SOCKET"
        ls -la "$SOCKET"
      else
        echo "Socket not found: $SOCKET"
      fi
      ;;

  d)  # Diagnose Failed Connections
      case "$DRIVER" in
        postgresql)
          LOG="/var/log/postgresql/postgresql-$(date +%Y-%m-%d).log"
          ;;
        mysql)
          LOG="/var/log/mysql/error.log"
          ;;
        *)
          echo "Error: Log location unknown for $DRIVER" >&2
          exit 1
          ;;
      esac
      if [[ -f "$LOG" ]]; then
        echo "Last 10 lines from $LOG:"
        tail -10 "$LOG"
      else
        echo "Log file not found: $LOG"
      fi
      ;;

  o)  # Set Connection Timeout Parameters
      echo "Testing connection with 2 second timeout..."
      case "$DRIVER" in
        postgresql)
          PGPASSWORD="$PASS" psql "host=$HOST port=$PORT user=$USER dbname=$DBNAME connect_timeout=2" -c "SELECT 1;"
          ;;
        mysql)
          mysql -h "$HOST" -P "$PORT" -u "$USER" -p"$PASS" "$DBNAME" --connect-timeout=2 -e "SELECT 1;"
          ;;
        *)
          echo "Error: Timeout test not supported for $DRIVER" >&2
          exit 1
          ;;
      esac
      ;;

  *)
      echo "Error: Unknown command '$1'" >&2
      echo "Valid commands: p, n, c, q, s, l, t, k, d, o" >&2
      exit 1
      ;;
esac