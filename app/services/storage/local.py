"""
Database Controller Module

This module provides a comprehensive Python interface to interact with the database control
bash script (dbctl.rc.sh) through a structured class-based approach. It wraps all functionality
of the original script while providing type hints, thorough documentation, and a more
Pythonic interface.
"""

from typing import List, Optional, Literal, Union, Dict, Any
import logging
from enum import Enum

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("DBController")

# Type definitions to enhance code readability and IDE support
DatabaseType = Literal["postgres", "mariadb", "mongodb", "influxdb", "neo4j", "redis"]
CommandType = Literal["s", "k", "r", "l", "b", "c", "h", "t"]
AllCommandType = Literal["s", "k", "t", "b"]

class DatabaseService(Enum):
    """Enum representing available database services and their command line flags."""
    POSTGRES = "p"
    MARIADB = "m"
    MONGODB = "g"
    INFLUXDB = "f"
    NEO4J = "n"
    REDIS = "r"

class DatabaseCommand(Enum):
    """Enum representing available commands for database services."""
    START = "s"
    STOP = "k"
    RESTART = "r"
    LOGS = "l"
    BACKUP = "b"
    CONNECT = "c"
    HEALTH = "h"
    STATS = "t"

class AllServicesCommand(Enum):
    """Enum representing commands that can be applied to all services at once."""
    START = "s"
    STOP = "k"
    STATUS = "t"
    BACKUP = "b"

class _DBController:
    """
    A Python class to interact with the dbctl.sh Terraform database stack control script.
    
    This class provides a clean, well-documented interface to all the functionality
    offered by the original bash script, including initializing the stack, controlling
    individual database services, and performing actions on all services at once.
    """
    
    def __init__(self, run_command_func: callable):
        """
        Initialize the DBController with a function to execute the underlying shell script.
        
        Args:
            run_command_func: A callable that accepts a list of command arguments and
                              executes the dbctl.sh script with those arguments. This
                              function should handle the actual command execution and
                              return the results.
        """
        self._run_command = run_command_func
        logger.info("DBController initialized")
        
    def initialize_stack(self, root_password: Optional[str] = None) -> Dict[str, Any]:
        """
        Initialize the database stack using Terraform.
        
        This is equivalent to running dbctl.sh -i [password]
        
        Args:
            root_password: Optional root password for the databases.
                           If not provided, the script may use default values
                           or prompt for input depending on its implementation.
                           
        Returns:
            Dictionary containing the results of the initialization operation.
            
        Raises:
            RuntimeError: If the initialization fails.
        """
        logger.info("Initializing database stack with Terraform")
        
        # Construct the command arguments
        args = ["-i"]
        if root_password:
            logger.debug("Root password provided")
            args.append(root_password)
            
        # Execute the command
        result = self._run_command(args)
        logger.info("Stack initialization completed")
        return result
    
    def manage_service(self, 
                       service: Union[DatabaseService, str], 
                       command: Union[DatabaseCommand, str]) -> Dict[str, Any]:
        """
        Execute a command on a specific database service.
        
        This is equivalent to running dbctl.sh -[service_flag] [command]
        
        Args:
            service: The database service to manage. Can be either a DatabaseService enum
                     value or a string representing the service flag ('p', 'm', 'g', etc.).
            command: The command to execute. Can be either a DatabaseCommand enum value
                     or a string representing the command ('s', 'k', 'r', etc.).
                     
        Returns:
            Dictionary containing the results of the operation.
            
        Raises:
            ValueError: If an invalid service or command is provided.
            RuntimeError: If the command execution fails.
        """
        # Convert enum values to their string representation if needed
        service_flag = service.value if isinstance(service, DatabaseService) else service
        cmd = command.value if isinstance(command, DatabaseCommand) else command
        
        # Validate inputs
        if service_flag not in [s.value for s in DatabaseService]:
            raise ValueError(f"Invalid service flag: {service_flag}")
        if cmd not in [c.value for c in DatabaseCommand]:
            raise ValueError(f"Invalid command: {cmd}")
            
        logger.info(f"Managing service with flag '{service_flag}', command '{cmd}'")
        
        # Execute the command
        result = self._run_command([f"-{service_flag}", cmd])
        logger.info(f"Service command executed: -{service_flag} {cmd}")
        return result
    
    def manage_all_services(self, command: Union[AllServicesCommand, str]) -> Dict[str, Any]:
        """
        Execute a command on all database services simultaneously.
        
        This is equivalent to running dbctl.sh -a [command]
        
        Args:
            command: The command to execute on all services. Can be either an AllServicesCommand 
                     enum value or a string representing the command ('s', 'k', 't', 'b').
                     
        Returns:
            Dictionary containing the results of the operation.
            
        Raises:
            ValueError: If an invalid command is provided.
            RuntimeError: If the command execution fails.
        """
        # Convert enum value to string if needed
        cmd = command.value if isinstance(command, AllServicesCommand) else command
        
        # Validate input
        if cmd not in [c.value for c in AllServicesCommand]:
            raise ValueError(f"Invalid command for all services: {cmd}")
            
        logger.info(f"Managing all services with command '{cmd}'")
        
        # Execute the command
        result = self._run_command(["-a", cmd])
        logger.info(f"All services command executed: -a {cmd}")
        return result
    
    # Convenience methods for common operations
    
    def start_service(self, service: Union[DatabaseService, str]) -> Dict[str, Any]:
        """
        Start a specific database service.
        
        Args:
            service: The database service to start.
                    
        Returns:
            Dictionary containing the results of the operation.
        """
        logger.info(f"Starting service: {service}")
        return self.manage_service(service, DatabaseCommand.START)
    
    def stop_service(self, service: Union[DatabaseService, str]) -> Dict[str, Any]:
        """
        Stop a specific database service.
        
        Args:
            service: The database service to stop.
                    
        Returns:
            Dictionary containing the results of the operation.
        """
        logger.info(f"Stopping service: {service}")
        return self.manage_service(service, DatabaseCommand.STOP)
    
    def restart_service(self, service: Union[DatabaseService, str]) -> Dict[str, Any]:
        """
        Restart a specific database service.
        
        Args:
            service: The database service to restart.
                    
        Returns:
            Dictionary containing the results of the operation.
        """
        logger.info(f"Restarting service: {service}")
        return self.manage_service(service, DatabaseCommand.RESTART)
    
    def view_logs(self, service: Union[DatabaseService, str]) -> Dict[str, Any]:
        """
        View logs for a specific database service.
        
        Args:
            service: The database service to view logs for.
                    
        Returns:
            Dictionary containing the logs and results of the operation.
        """
        logger.info(f"Viewing logs for service: {service}")
        return self.manage_service(service, DatabaseCommand.LOGS)
    
    def backup_database(self, service: Union[DatabaseService, str]) -> Dict[str, Any]:
        """
        Backup a specific database.
        
        Args:
            service: The database service to backup.
                    
        Returns:
            Dictionary containing the results of the backup operation.
        """
        logger.info(f"Backing up database: {service}")
        return self.manage_service(service, DatabaseCommand.BACKUP)
    
    def connect_to_cli(self, service: Union[DatabaseService, str]) -> Dict[str, Any]:
        """
        Connect to the command-line interface of a specific database.
        
        Args:
            service: The database service to connect to.
                    
        Returns:
            Dictionary containing the results of the connection operation.
        """
        logger.info(f"Connecting to CLI for service: {service}")
        return self.manage_service(service, DatabaseCommand.CONNECT)
    
    def check_health(self, service: Union[DatabaseService, str]) -> Dict[str, Any]:
        """
        Check the health status of a specific database service.
        
        Args:
            service: The database service to check health for.
                    
        Returns:
            Dictionary containing the health information and results of the operation.
        """
        logger.info(f"Checking health for service: {service}")
        return self.manage_service(service, DatabaseCommand.HEALTH)
    
    def show_statistics(self, service: Union[DatabaseService, str]) -> Dict[str, Any]:
        """
        Show statistics for a specific database service.
        
        Args:
            service: The database service to show statistics for.
                    
        Returns:
            Dictionary containing the statistics and results of the operation.
        """
        logger.info(f"Showing statistics for service: {service}")
        return self.manage_service(service, DatabaseCommand.STATS)
    
    def start_all_services(self) -> Dict[str, Any]:
        """
        Start all database services at once.
                    
        Returns:
            Dictionary containing the results of the operation.
        """
        logger.info("Starting all services")
        return self.manage_all_services(AllServicesCommand.START)
    
    def stop_all_services(self) -> Dict[str, Any]:
        """
        Stop all database services at once.
                    
        Returns:
            Dictionary containing the results of the operation.
        """
        logger.info("Stopping all services")
        return self.manage_all_services(AllServicesCommand.STOP)
    
    def show_all_statistics(self) -> Dict[str, Any]:
        """
        Show statistics for all database services.
                    
        Returns:
            Dictionary containing the statistics and results of the operation.
        """
        logger.info("Showing statistics for all services")
        return self.manage_all_services(AllServicesCommand.STATUS)
    
    def backup_all_databases(self) -> Dict[str, Any]:
        """
        Backup all databases at once.
                    
        Returns:
            Dictionary containing the results of the backup operations.
        """
        logger.info("Backing up all databases")
        return self.manage_all_services(AllServicesCommand.BACKUP)

def _run_function(args: List[str]) -> Dict[str, Any]:
        """a function to run the dbctl.rc.sh script."""
        from core.utils.scripts import run_db_ctl_rc
        return run_db_ctl_rc(args) 

local_db_controller = _DBController(_run_function)
