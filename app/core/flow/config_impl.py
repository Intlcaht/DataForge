import yaml
import os
import sys
from typing import Dict, List, Optional
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('db_manager')

# Database System Detection Functions
def get_supported_db_engines(config: Dict) -> List[str]:
    """
    Get a list of all database engines defined in the configuration.
    
    Args:
        config: Configuration dictionary
        
    Returns:
        List of database engine names
    """
    return list(config.get('storage', {}).keys())

def get_databases_by_engine(config: Dict, engine: str) -> Dict:
    """
    Get all databases for a specific engine.
    
    Args:
        config: Configuration dictionary
        engine: Database engine name
        
    Returns:
        Dictionary of databases for the specified engine
    """
    return config.get('storage', {}).get(engine, {}).get('databases', {})

def get_all_databases(config: Dict) -> Dict[str, Dict]:
    """
    Get all databases from all engines with their configurations.
    
    Args:
        config: Configuration dictionary
        
    Returns:
        Dictionary mapping database names to their configurations
    """
    all_dbs = {}
    for engine in get_supported_db_engines(config):
        for db_name, db_config in get_databases_by_engine(config, engine).items():
            all_dbs[db_name] = {
                'engine': engine,
                'config': db_config
            }
    return all_dbs

def get_database_engine(config: Dict, db_name: str) -> Optional[str]:
    """
    Find which engine a database belongs to.
    
    Args:
        config: Configuration dictionary
        db_name: Database name
        
    Returns:
        Engine name or None if not found
    """
    for engine in get_supported_db_engines(config):
        if db_name in get_databases_by_engine(config, engine):
            return engine
    return None

# Location Management Functions
def get_db_location(config: Dict, db_name: str) -> Optional[str]:
    """
    Get the location name for a specific database.
    
    Args:
        config: Configuration dictionary
        db_name: Database name
        
    Returns:
        Location name or None if not found
    """
    engine = get_database_engine(config, db_name)
    if not engine:
        return None
    
    db_config = get_databases_by_engine(config, engine).get(db_name, {})
    return db_config.get('location')

def get_location_config(config: Dict, engine: str, location_name: str) -> Optional[Dict]:
    """
    Get configuration for a specific location.
    
    Args:
        config: Configuration dictionary
        engine: Database engine name
        location_name: Location name
        
    Returns:
        Location configuration or None if not found
    """
    return config.get('storage', {}).get(engine, {}).get('locations', {}).get(location_name)

def get_all_locations(config: Dict, engine: str = None) -> Dict:
    """
    Get all location configurations, optionally filtered by engine.
    
    Args:
        config: Configuration dictionary
        engine: Optional database engine to filter by
        
    Returns:
        Dictionary mapping location names to their configurations
    """
    locations = {}
    engines = [engine] if engine else get_supported_db_engines(config)
    
    for eng in engines:
        eng_locations = config.get('storage', {}).get(eng, {}).get('locations', {})
        for loc_name, loc_config in eng_locations.items():
            if isinstance(loc_config, dict):  # Skip non-dictionary values like admin credentials
                locations[f"{eng}:{loc_name}"] = {
                    'engine': eng,
                    'name': loc_name,
                    'config': loc_config
                }
    return locations

def get_connection_info(config: Dict, db_name: str) -> Optional[Dict]:
    """
    Get connection information for a database including engine, host, port, etc.
    
    Args:
        config: Configuration dictionary
        db_name: Database name
        
    Returns:
        Connection information dictionary or None if not found
    """
    engine = get_database_engine(config, db_name)
    if not engine:
        return None
    
    db_config = get_databases_by_engine(config, engine).get(db_name, {})
    location_name = db_config.get('location')
    
    if not location_name:
        return None
    
    location = get_location_config(config, engine, location_name)
    if not location:
        return None
    
    # Common connection info
    connection_info = {
        'engine': engine,
        'host': location.get('host'),
        'port': location.get('port'),
        'location_name': location_name
    }
    
    # Add engine-specific admin credentials
    if engine == 'postgres' or engine == 'mariadb':
        connection_info.update({
            'admin': location.get('admin'),
            'admin_password': location.get('admin_password')
        })
    elif engine == 'mongodb':
        connection_info.update({
            'admin': location.get('admin'),
            'admin_password': location.get('admin_password')
        })
    elif engine == 'redis':
        connection_info.update({
            'admin_password': location.get('admin_password')
        })
    elif engine == 'influxdb':
        connection_info.update({
            'admin_token': location.get('admin_token')
        })
    elif engine == 'neo4j':
        # Neo4j has admin credentials at the engine level
        admin_creds = {
            'admin': config.get('storage', {}).get('neo4j', {}).get('locations', {}).get('admin'),
            'admin_password': config.get('storage', {}).get('neo4j', {}).get('locations', {}).get('admin_password')
        }
        connection_info.update(admin_creds)
    
    return connection_info

# User Management Functions
def list_db_users(config: Dict, db_name: str) -> List[Dict]:
    """
    Get all users for a specific database.
    
    Args:
        config: Configuration dictionary
        db_name: Database name
        
    Returns:
        List of user configurations
    """
    engine = get_database_engine(config, db_name)
    if not engine:
        return []
    
    db_config = get_databases_by_engine(config, engine).get(db_name, {})
    return db_config.get('users', [])

def get_user_info(config: Dict, db_name: str, username: str) -> Optional[Dict]:
    """
    Get information about a specific user in a database.
    
    Args:
        config: Configuration dictionary
        db_name: Database name
        username: Username to look for
        
    Returns:
        User configuration or None if not found
    """
    users = list_db_users(config, db_name)
    for user in users:
        if user.get('username') == username:
            return user
    return None

def get_all_users(config: Dict) -> Dict:
    """
    Get all users across all databases.
    
    Args:
        config: Configuration dictionary
        
    Returns:
        Dictionary mapping user identifiers to their configurations
    """
    all_users = {}
    all_dbs = get_all_databases(config)
    
    for db_name, db_info in all_dbs.items():
        engine = db_info['engine']
        users = list_db_users(config, db_name)
        
        for user in users:
            username = user.get('username', 'anonymous')
            user_id = f"{engine}:{db_name}:{username}"
            all_users[user_id] = {
                'engine': engine,
                'database': db_name,
                'config': user
            }
    
    return all_users

# Scaling Configuration Functions
def get_scaling_config(config: Dict, db_name: str) -> Optional[Dict]:
    """
    Get scaling configuration for a database's location.
    
    Args:
        config: Configuration dictionary
        db_name: Database name
        
    Returns:
        Scaling configuration or None if not found
    """
    engine = get_database_engine(config, db_name)
    if not engine:
        return None
    
    db_config = get_databases_by_engine(config, engine).get(db_name, {})
    location_name = db_config.get('location')
    
    if not location_name:
        return None
    
    location = get_location_config(config, engine, location_name)
    if not location:
        return None
    
    return location.get('scaling', {})

def get_autoscaling_databases(config: Dict) -> List[str]:
    """
    Get all databases that have autoscaling enabled.
    
    Args:
        config: Configuration dictionary
        
    Returns:
        List of database names with autoscaling enabled
    """
    autoscaling_dbs = []
    all_dbs = get_all_databases(config)
    
    for db_name in all_dbs:
        scaling = get_scaling_config(config, db_name)
        if scaling and scaling.get('auto_scaling'):
            autoscaling_dbs.append(db_name)
    
    return autoscaling_dbs

# Control Functions
def get_database_controls(config: Dict, db_name: str) -> List[Dict]:
    """
    Get control configurations for a database's engine.
    
    Args:
        config: Configuration dictionary
        db_name: Database name
        
    Returns:
        List of control configurations
    """
    engine = get_database_engine(config, db_name)
    if not engine:
        return []
    
    return config.get('storage', {}).get(engine, {}).get('controls', [])

def get_migration_file_location(config: Dict, db_name: str) -> Optional[str]:
    """
    Get migration file location for a database.
    
    Args:
        config: Configuration dictionary
        db_name: Database name
        
    Returns:
        Migration file location or None if not found
    """
    controls = get_database_controls(config, db_name)
    
    for control in controls:
        if control.get('name') == 'migration_files':
            return control.get('location')
    
    return None

def get_global_controls(config: Dict) -> Dict:
    """
    Get global control configurations.
    
    Args:
        config: Configuration dictionary
        
    Returns:
        Dictionary of global controls
    """
    return config.get('controls', {})

def get_environment_controls(config: Dict, environment: str = None) -> Dict:
    """
    Get environment-specific control configurations.
    
    Args:
        config: Configuration dictionary
        environment: Environment name or None for current environment
        
    Returns:
        Dictionary of environment-specific controls
    """
    if not environment:
        environment = config.get('metadata', {}).get('environment', 'development')
    
    return config.get('environments', {}).get(environment, {}).get('controls', {})

# Environment Functions
def get_current_environment(config: Dict) -> str:
    """
    Get the name of the current environment.
    
    Args:
        config: Configuration dictionary
        
    Returns:
        Current environment name
    """
    return config.get('metadata', {}).get('environment', 'development')

def get_backup_schedule(config: Dict, environment: str = None) -> str:
    """
    Get backup schedule for the specified environment.
    
    Args:
        config: Configuration dictionary
        environment: Environment name or None for current environment
        
    Returns:
        Backup schedule
    """
    if not environment:
        environment = get_current_environment(config)
    
    return config.get('environments', {}).get(environment, {}).get('backup_schedule', 'daily')

# Database Command Generation Functions
def get_postgres_connection_string(connection_info: Dict, db_name: str = None, username: str = None, password: str = None) -> str:
    """
    Generate a PostgreSQL connection string.
    
    Args:
        connection_info: Connection information dictionary
        db_name: Optional database name
        username: Optional username
        password: Optional password
        
    Returns:
        PostgreSQL connection string
    """
    user = username or connection_info.get('admin')
    pwd = password or connection_info.get('admin_password')
    db = db_name or 'postgres'  # Default to postgres database if none specified
    
    return f"postgresql://{user}:{pwd}@{connection_info.get('host')}:{connection_info.get('port')}/{db}"

def get_mariadb_connection_params(connection_info: Dict, db_name: str = None, username: str = None, password: str = None) -> List[str]:
    """
    Generate MariaDB/MySQL connection parameters.
    
    Args:
        connection_info: Connection information dictionary
        db_name: Optional database name
        username: Optional username
        password: Optional password
        
    Returns:
        List of connection parameters for mysql client
    """
    params = [
        '-h', connection_info.get('host'),
        '-P', str(connection_info.get('port')),
        '-u', username or connection_info.get('admin')
    ]
    
    pwd = password or connection_info.get('admin_password')
    if pwd:
        params.extend(['--password=' + pwd])
    
    if db_name:
        params.append(db_name)
    
    return params

def get_mongodb_connection_string(connection_info: Dict, db_name: str = None, username: str = None, password: str = None) -> str:
    """
    Generate a MongoDB connection string.
    
    Args:
        connection_info: Connection information dictionary
        db_name: Optional database name
        username: Optional username
        password: Optional password
        
    Returns:
        MongoDB connection string
    """
    user = username or connection_info.get('admin')
    pwd = password or connection_info.get('admin_password')
    auth_part = f"{user}:{pwd}@" if user and pwd else ""
    db_part = f"/{db_name}" if db_name else ""
    
    return f"mongodb://{auth_part}{connection_info.get('host')}:{connection_info.get('port')}{db_part}"

def get_redis_connection_params(connection_info: Dict, password: str = None) -> List[str]:
    """
    Generate Redis connection parameters.
    
    Args:
        connection_info: Connection information dictionary
        password: Optional password
        
    Returns:
        List of connection parameters for redis-cli
    """
    params = [
        '-h', connection_info.get('host'),
        '-p', str(connection_info.get('port'))
    ]
    
    pwd = password or connection_info.get('admin_password')
    if pwd:
        params.extend(['-a', pwd])
    
    return params

def get_neo4j_connection_params(connection_info: Dict, username: str = None, password: str = None) -> Dict:
    """
    Generate Neo4j connection parameters.
    
    Args:
        connection_info: Connection information dictionary
        username: Optional username
        password: Optional password
        
    Returns:
        Dictionary of Neo4j connection parameters
    """
    return {
        'uri': f"bolt://{connection_info.get('host')}:{connection_info.get('port')}",
        'auth': (
            username or connection_info.get('admin'),
            password or connection_info.get('admin_password')
        )
    }

def get_influxdb_connection_params(connection_info: Dict, token: str = None) -> Dict:
    """
    Generate InfluxDB connection parameters.
    
    Args:
        connection_info: Connection information dictionary
        token: Optional authentication token
        
    Returns:
        Dictionary of InfluxDB connection parameters
    """
    return {
        'url': f"http://{connection_info.get('host')}:{connection_info.get('port')}",
        'token': token or connection_info.get('admin_token')
    }
