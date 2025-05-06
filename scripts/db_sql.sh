#!/bin/bash

# SQL Database Management Script
# Supports PostgreSQL, MySQL, and SQLite
# Usage: sql_tool.sh [COMMAND] [OPTIONS]
# 
# Commands:
#   -i  Initialize new database
#   -u  Create user
#   -g  Grant privileges
#   -r  Run SQL script
#   -m  Import CSV
#   -e  Export CSV
#   -b  Backup database
#   -s  Restore database
#   -k  Drop database
#   -l  List databases/tables
#   -v  View table schema
#   -q  Run SQL query
#   -h  Show help
# 
# Options:
#   -d  Database name
#   -t  Database type (postgres|mysql|sqlite)
#   -n  Username
#   -p  Password
#   -f  File path
#   -T  Table name
#   -q  SQL query (with -q command)
# 
# Examples:
#   Initialize PostgreSQL DB: sql_tool.sh -i -d db -t postgres
#   Create MySQL user:        sql_tool.sh -u -n user -p pass -t mysql
#   Run SQLite script:        sql_tool.sh -r -d db -f script.sql -t sqlite
#   Import CSV to SQLite:     sql_tool.sh -m -d db -T table -f data.csv -t sqlite
#   Backup MySQL DB:          sql_tool.sh -b -d db -t mysql
#   Show PostgreSQL schema:   sql_tool.sh -v -d db -T table -t postgres

# Initialize variables
command=; dbname=; dbtype=; username=; password=; file=; table=; query=

# Parse command line options
while getopts "iugrmebsklvqhd:t:n:p:f:T:q:" opt; do
  case $opt in
    i|u|g|r|m|e|b|s|k|l|v|q|h) command=$opt ;;
    d) dbname=$OPTARG ;;
    t) dbtype=$OPTARG ;;
    n) username=$OPTARG ;;
    p) password=$OPTARG ;;
    f) file=$OPTARG ;;
    T) table=$OPTARG ;;
    q) query=$OPTARG ;;
    *) echo "Invalid option: -$OPTARG"; exit 1 ;;
  esac
done

show_help() {
  sed -n '/^# /,/^$/p' "$0" | sed 's/^# //'
}

execute_command() {
  case $1 in
    i) # Initialize database
      case $dbtype in
        postgres) createdb --encoding=UTF8 "$dbname" ;;
        mysql) mysql -u root -e "CREATE DATABASE $dbname CHARSET utf8mb4 COLLATE utf8mb4_unicode_ci" ;;
        sqlite) sqlite3 "$dbname.db" .quit ;;
      esac ;;

    u) # Create user
      case $dbtype in
        postgres) psql -c "CREATE USER $username WITH PASSWORD '$password'" ;;
        mysql) mysql -u root -e "CREATE USER '$username'@'localhost' IDENTIFIED BY '$password'" ;;
        sqlite) echo "SQLite uses file system permissions" ;;
      esac ;;

    g) # Grant privileges
      case $dbtype in
        postgres) psql -c "GRANT ALL PRIVILEGES ON DATABASE $dbname TO $username" ;;
        mysql) mysql -u root -e "GRANT ALL PRIVILEGES ON $dbname.* TO '$username'@'localhost'" ;;
        sqlite) echo "SQLite permissions not supported" ;;
      esac ;;

    r) # Run SQL script
      case $dbtype in
        postgres) psql -d "$dbname" -f "$file" ;;
        mysql) mysql "$dbname" < "$file" ;;
        sqlite) sqlite3 "$dbname.db" < "$file" ;;
      esac ;;

    m) # Import CSV
      case $dbtype in
        postgres) psql -d "$dbname" -c "COPY $table FROM STDIN CSV HEADER" < "$file" ;;
        mysql) mysqlimport --ignore-lines=1 --fields-terminated-by=, "$dbname" "$file" ;;
        sqlite) sqlite3 "$dbname.db" ".mode csv" ".import $file $table" ;;
      esac ;;

    e) # Export CSV
      case $dbtype in
        postgres) psql -d "$dbname" -c "\COPY (SELECT * FROM $table) TO STDOUT CSV HEADER" > "$file" ;;
        mysql) mysql "$dbname" -e "SELECT * FROM $table INTO OUTFILE '$file' FIELDS TERMINATED BY ','" ;;
        sqlite) sqlite3 "$dbname.db" ".headers on" ".mode csv" ".output $file" "SELECT * FROM $table;" ;;
      esac ;;

    b) # Backup database
      case $dbtype in
        postgres) pg_dump "$dbname" > "${dbname}_backup.sql" ;;
        mysql) mysqldump "$dbname" > "${dbname}_backup.sql" ;;
        sqlite) sqlite3 "$dbname.db" ".dump" > "${dbname}_backup.sql" ;;
      esac ;;

    s) # Restore database
      case $dbtype in
        postgres) psql -d "$dbname" < "$file" ;;
        mysql) mysql "$dbname" < "$file" ;;
        sqlite) sqlite3 "$dbname.db" < "$file" ;;
      esac ;;

    k) # Drop database
      case $dbtype in
        postgres) dropdb "$dbname" ;;
        mysql) mysql -e "DROP DATABASE $dbname" ;;
        sqlite) rm -f "$dbname.db" ;;
      esac ;;

    l) # List databases/tables
      case $dbtype in
        postgres) psql -c "\l"; psql -d "$dbname" -c "\dt" ;;
        mysql) mysql -e "SHOW DATABASES; USE $dbname; SHOW TABLES" ;;
        sqlite) sqlite3 "$dbname.db" ".databases" ".tables" ;;
      esac ;;

    v) # View schema
      case $dbtype in
        postgres) psql -d "$dbname" -c "\d $table" ;;
        mysql) mysql -e "DESCRIBE $dbname.$table" ;;
        sqlite) sqlite3 "$dbname.db" ".schema $table" ;;
      esac ;;

    q) # Run query
      case $dbtype in
        postgres) psql -d "$dbname" -c "$query" ;;
        mysql) mysql -e "USE $dbname; $query" ;;
        sqlite) sqlite3 "$dbname.db" "$query" ;;
      esac ;;

    h) show_help ;;
  esac
}

# Validate and execute
if [ "$command" = h ]; then
  show_help
elif [ -z "$command" ]; then
  echo "Error: No command specified"
  show_help
  exit 1
else
  execute_command $command
fi