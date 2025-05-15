import yaml
import os
import sys
from typing import Dict

class ConfigStructureError(Exception):
    """Raised when the configuration file is missing required keys or structure."""
    pass

def validate_config_structure(config):
    # Top-level required keys
    required_top_keys = ['storage', 'controls', 'environments']
    for key in required_top_keys:
        if key not in config:
            raise ConfigStructureError(f"Missing top-level key: '{key}' in config.")

    # Validate 'storage'
    if not isinstance(config['storage'], dict):
        raise ConfigStructureError("'storage' must be a dictionary.")
    for engine, engine_data in config['storage'].items():
        if not isinstance(engine_data, dict):
            raise ConfigStructureError(f"'storage.{engine}' must be a dictionary.")
        if 'databases' not in engine_data:
            raise ConfigStructureError(f"'databases' missing in 'storage.{engine}'.")
        if not isinstance(engine_data['databases'], dict):
            raise ConfigStructureError(f"'storage.{engine}.databases' must be a dictionary.")
        for db_name, db_data in engine_data['databases'].items():
            if not isinstance(db_data, dict):
                raise ConfigStructureError(f"'storage.{engine}.databases.{db_name}' must be a dictionary.")
            if 'location' not in db_data:
                raise ConfigStructureError(f"'location' missing in 'storage.{engine}.databases.{db_name}'.")
            if not isinstance(db_data['location'], str):
                raise ConfigStructureError(f"'location' in 'storage.{engine}.databases.{db_name}' must be a string.")
            if 'users' in db_data and not isinstance(db_data['users'], list):
                raise ConfigStructureError(f"'users' in 'storage.{engine}.databases.{db_name}' must be a list.")

        if 'controls' in engine_data and not isinstance(engine_data['controls'], list):
            raise ConfigStructureError(f"'controls' in 'storage.{engine}' must be a list.")

    # Validate 'controls'
    if not isinstance(config['controls'], dict):
        raise ConfigStructureError("'controls' must be a dictionary.")
    for control, control_data in config['controls'].items():
        if not isinstance(control_data, dict):
            raise ConfigStructureError(f"'controls.{control}' must be a dictionary.")
        if 'enabled' not in control_data:
            raise ConfigStructureError(f"'enabled' missing in 'controls.{control}'.")
        if not isinstance(control_data['enabled'], bool):
            raise ConfigStructureError(f"'enabled' in 'controls.{control}' must be a boolean.")

    # Validate 'environments'
    if not isinstance(config['environments'], dict):
        raise ConfigStructureError("'environments' must be a dictionary.")
    for env, env_data in config['environments'].items():
        if not isinstance(env_data, dict):
            raise ConfigStructureError(f"'environments.{env}' must be a dictionary.")

import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('db_manager')

# Configuration Functions
def load_config(config_file: str) -> Dict:
    """
    Load configuration from YAML file.
    
    Args:
        config_file: Path to the YAML configuration file
        
    Returns:
        Dict containing the configuration
    """
    try:
        if not os.path.exists(config_file):
            logger.error(f"Configuration file not found: {config_file}")
            sys.exit(1)
            
        with open(config_file, 'r') as file:
            config = yaml.safe_load(file)
        validate_config_structure(config)
        logger.info(f"Configuration loaded from {config_file}")
        return config
    except yaml.YAMLError as e:
        logger.error(f"Error parsing YAML configuration: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Error loading configuration: {e}")
        sys.exit(1)