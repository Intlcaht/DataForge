"""
DatabaseScript: A comprehensive wrapper for the database management bash script.

This module provides a clean Python interface to interact with the underlying
bash script that handles various database operations including provisioning,
backup, restore, and advanced management features.

Date: April 12, 2025
"""

import os
import logging
from typing import List, Optional, Any, Callable


class _DatabaseScript:
    """
    A comprehensive wrapper class for interacting with the database management script.
    
    This class provides methods that map to all functionality of the underlying bash script,
    with proper parameter validation, error handling, and logging.
    """
    
    def __init__(self, run_sh: Callable, verbose: bool = False):
        """
        Initialize the DatabaseScript wrapper.
        
        Args:
            run_sh: Function to execute the script with provided arguments
            verbose: Enable verbose logging (default: False)
        """
        # Store the provided run_sh function
        self.run_sh = run_sh
        self.verbose = verbose
        
        # Configure logging
        log_level = logging.DEBUG if verbose else logging.INFO
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger('DatabaseManagement')
        
        self.logger.info("DatabaseScript initialized")
    
    # Helper method to properly format and execute commands
    def _execute(self, args: List[str]) -> Any:
        """
        Format and execute the command with the provided arguments.
        
        Args:
            args: List of command-line arguments
            
        Returns:
            Result from the run_sh function
        """
        # Convert argument list to a single string with proper spacing
        cmd_str = ' '.join(args)
        
        self.logger.debug(f"Executing: {cmd_str}")
        
        try:
            # Execute the command using the provided run_sh function
            result = self.run_sh([cmd_str])
            return result
        except Exception as e:
            self.logger.error(f"Exception running command: {str(e)}")
            raise
    
    # Basic Operations
    
    def provision_databases(self, config_file: Optional[str] = None) -> bool:
        """
        Provision databases from configuration file.
        
        Args:
            config_file: Optional custom config file path
        
        Returns:
            True if successful, False otherwise
        """
        args = []
        
        # Add custom config file if provided
        if config_file:
            args.extend(["-c", config_file])
        
        # Add provision flag
        args.append("-p")
        
        self.logger.info(f"Provisioning databases" + 
                         (f" with config {config_file}" if config_file else ""))
        
        # Execute and return result (assuming run_sh returns success/failure)
        return self._execute(args)
    
    def clear_data(self, database_id: str) -> bool:
        """
        Clear data from a specific database.
        
        Args:
            database_id: Database identifier in format <db_type>.<db_name>
        
        Returns:
            True if successful, False otherwise
        """
        # Validate database identifier format
        if '.' not in database_id:
            self.logger.error(f"Invalid database ID format: {database_id}. Expected format: <db_type>.<db_name>")
            return False
        
        args = ["-C", "-d", database_id]
        
        self.logger.info(f"Clearing data from database: {database_id}")
        
        return self._execute(args)
    
    def backup_database(self, database_id: str, backup_path: str) -> bool:
        """
        Backup a database to the specified path.
        
        Args:
            database_id: Database identifier in format <db_type>.<db_name>
            backup_path: Path where backup will be stored
        
        Returns:
            True if successful, False otherwise
        """
        # Validate database identifier format
        if '.' not in database_id:
            self.logger.error(f"Invalid database ID format: {database_id}. Expected format: <db_type>.<db_name>")
            return False
        
        # Create directory for backup if it doesn't exist
        backup_dir = os.path.dirname(backup_path)
        if backup_dir and not os.path.exists(backup_dir):
            os.makedirs(backup_dir)
            self.logger.debug(f"Created backup directory: {backup_dir}")
        
        args = ["-b", "-d", database_id, backup_path]
        
        self.logger.info(f"Backing up database {database_id} to {backup_path}")
        
        return self._execute(args)
    
    def restore_database(self, database_id: str, backup_path: str) -> bool:
        """
        Restore a database from a backup file.
        
        Args:
            database_id: Database identifier in format <db_type>.<db_name>
            backup_path: Path to the backup file
        
        Returns:
            True if successful, False otherwise
        """
        # Validate database identifier format
        if '.' not in database_id:
            self.logger.error(f"Invalid database ID format: {database_id}. Expected format: <db_type>.<db_name>")
            return False
        
        # Check if backup file exists
        if not os.path.isfile(backup_path):
            self.logger.error(f"Backup file not found: {backup_path}")
            return False
        
        args = ["-r", "-d", database_id, backup_path]
        
        self.logger.info(f"Restoring database {database_id} from {backup_path}")
        
        return self._execute(args)
    
    def delete_database(self, database_id: str) -> bool:
        """
        Delete a database.
        
        Args:
            database_id: Database identifier in format <db_type>.<db_name>
        
        Returns:
            True if successful, False otherwise
        """
        # Validate database identifier format
        if '.' not in database_id:
            self.logger.error(f"Invalid database ID format: {database_id}. Expected format: <db_type>.<db_name>")
            return False
        
        args = ["-D", "-d", database_id]
        
        self.logger.info(f"Deleting database: {database_id}")
        
        return self._execute(args)
    
    def show_help(self) -> Any:
        """
        Display help information from the script.
        
        Returns:
            Help text as returned by run_sh
        """
        args = ["-h"]
        
        self.logger.info("Displaying script help")
        
        return self._execute(args)
    
    # Extended Operations
    
    def validate_config(self) -> bool:
        """
        Validate the configuration file.
        
        Returns:
            True if valid, False otherwise
        """
        args = ["--validate"]
        
        self.logger.info("Validating configuration file")
        
        return self._execute(args)
    
    def check_schema_drift(self, database_id: str) -> Any:
        """
        Detect schema drift for a database.
        
        Args:
            database_id: Database identifier in format <db_type>.<db_name>
        
        Returns:
            Result from run_sh
        """
        # Validate database identifier format
        if '.' not in database_id:
            self.logger.error(f"Invalid database ID format: {database_id}. Expected format: <db_type>.<db_name>")
            return False
        
        args = ["--drift-check", "-d", database_id]
        
        self.logger.info(f"Checking schema drift for database: {database_id}")
        
        return self._execute(args)
    
    def rotate_secrets(self, database_id: str) -> bool:
        """
        Rotate secrets for a database.
        
        Args:
            database_id: Database identifier in format <db_type>.<db_name>
        
        Returns:
            True if successful, False otherwise
        """
        # Validate database identifier format
        if '.' not in database_id:
            self.logger.error(f"Invalid database ID format: {database_id}. Expected format: <db_type>.<db_name>")
            return False
        
        args = ["--rotate-secrets", "-d", database_id]
        
        self.logger.info(f"Rotating secrets for database: {database_id}")
        
        return self._execute(args)
    
    def mask_production_data(self, database_id: str, target_env: str) -> bool:
        """
        Mask production data for use in another environment.
        
        Args:
            database_id: Database identifier in format <db_type>.<db_name>
            target_env: Target environment (e.g., staging, development)
        
        Returns:
            True if successful, False otherwise
        """
        # Validate database identifier format
        if '.' not in database_id:
            self.logger.error(f"Invalid database ID format: {database_id}. Expected format: <db_type>.<db_name>")
            return False
        
        args = ["--mask-data", "-d", database_id, "--target-env", target_env]
        
        self.logger.info(f"Masking production data for database {database_id} for use in {target_env}")
        
        return self._execute(args)
    
    def simulate_disaster_recovery(self, database_id: str) -> Any:
        """
        Simulate disaster recovery for a database.
        
        Args:
            database_id: Database identifier in format <db_type>.<db_name>
        
        Returns:
            Result from run_sh
        """
        # Validate database identifier format
        if '.' not in database_id:
            self.logger.error(f"Invalid database ID format: {database_id}. Expected format: <db_type>.<db_name>")
            return False
        
        args = ["--simulate-dr", "-d", database_id]
        
        self.logger.info(f"Simulating disaster recovery for database: {database_id}")
        
        return self._execute(args)
    
    def generate_schema_documentation(self, database_id: str, output_path: str) -> bool:
        """
        Generate schema documentation for a database.
        
        Args:
            database_id: Database identifier in format <db_type>.<db_name>
            output_path: Path where documentation will be saved
        
        Returns:
            True if successful, False otherwise
        """
        # Validate database identifier format
        if '.' not in database_id:
            self.logger.error(f"Invalid database ID format: {database_id}. Expected format: <db_type>.<db_name>")
            return False
        
        # Create output directory if it doesn't exist
        output_dir = os.path.dirname(output_path)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)
            self.logger.debug(f"Created output directory: {output_dir}")
        
        args = ["--doc-schema", "-d", database_id, "--output", output_path]
        
        self.logger.info(f"Generating schema documentation for {database_id} to {output_path}")
        
        return self._execute(args)
    
    def tag_environment(self, env: str) -> bool:
        """
        Tag the current environment.
        
        Args:
            env: Environment name (e.g., production, staging)
        
        Returns:
            True if successful, False otherwise
        """
        args = ["--tag-env", "--env", env]
        
        self.logger.info(f"Tagging environment as: {env}")
        
        return self._execute(args)
    
    def trigger_alert_test(self, database_id: str, scenario: str) -> bool:
        """
        Trigger a monitoring alert test for a database.
        
        Args:
            database_id: Database identifier in format <db_type>.<db_name>
            scenario: Alert scenario to test (e.g., high_latency)
        
        Returns:
            True if successful, False otherwise
        """
        # Validate database identifier format
        if '.' not in database_id:
            self.logger.error(f"Invalid database ID format: {database_id}. Expected format: <db_type>.<db_name>")
            return False
        
        args = ["--trigger-alert", "-d", database_id, "--scenario", scenario]
        
        self.logger.info(f"Triggering alert test for database {database_id} with scenario {scenario}")
        
        return self._execute(args)
    
    def create_sandbox(self, database_id: str, ttl: str) -> bool:
        """
        Create a sandbox database for testing.
        
        Args:
            database_id: Database identifier in format <db_type>.<db_name>
            ttl: Time-to-live for the sandbox (e.g., 2h, 1d)
        
        Returns:
            True if successful, False otherwise
        """
        # Validate database identifier format
        if '.' not in database_id:
            self.logger.error(f"Invalid database ID format: {database_id}. Expected format: <db_type>.<db_name>")
            return False
        
        args = ["--sandbox", "-d", database_id, "--ttl", ttl]
        
        self.logger.info(f"Creating sandbox for database {database_id} with TTL {ttl}")
        
        return self._execute(args)
    
    def manage_rbac(self, database_id: str, enable: bool) -> bool:
        """
        Enable or disable RBAC for a database.
        
        Args:
            database_id: Database identifier in format <db_type>.<db_name>
            enable: True to enable RBAC, False to disable
        
        Returns:
            True if successful, False otherwise
        """
        # Validate database identifier format
        if '.' not in database_id:
            self.logger.error(f"Invalid database ID format: {database_id}. Expected format: <db_type>.<db_name>")
            return False
        
        args = ["--rbac", "--enable" if enable else "--disable", "-d", database_id]
        
        action = "Enabling" if enable else "Disabling"
        self.logger.info(f"{action} RBAC for database: {database_id}")
        
        return self._execute(args)
    
    def apply_retention_policy(self, database_id: str, days: int) -> bool:
        """
        Apply a data retention policy to a database.
        
        Args:
            database_id: Database identifier in format <db_type>.<db_name>
            days: Number of days to retain data
        
        Returns:
            True if successful, False otherwise
        """
        # Validate database identifier format
        if '.' not in database_id:
            self.logger.error(f"Invalid database ID format: {database_id}. Expected format: <db_type>.<db_name>")
            return False
        
        args = ["--retention-policy", "--days", str(days), "-d", database_id]
        
        self.logger.info(f"Applying {days}-day retention policy to database: {database_id}")
        
        return self._execute(args)
    
    def check_cost_estimates(self, database_id: str) -> Any:
        """
        Check cost estimates for a database.
        
        Args:
            database_id: Database identifier in format <db_type>.<db_name>
        
        Returns:
            Result from run_sh
        """
        # Validate database identifier format
        if '.' not in database_id:
            self.logger.error(f"Invalid database ID format: {database_id}. Expected format: <db_type>.<db_name>")
            return False
        
        args = ["--check-cost", "-d", database_id]
        
        self.logger.info(f"Checking cost estimates for database: {database_id}")
        
        return self._execute(args)
    
    def test_auth_policy(self, database_id: str) -> Any:
        """
        Test authentication policy for a database.
        
        Args:
            database_id: Database identifier in format <db_type>.<db_name>
        
        Returns:
            Result from run_sh
        """
        # Validate database identifier format
        if '.' not in database_id:
            self.logger.error(f"Invalid database ID format: {database_id}. Expected format: <db_type>.<db_name>")
            return False
        
        args = ["--test-auth-policy", "-d", database_id]
        
        self.logger.info(f"Testing auth policy for database: {database_id}")
        
        return self._execute(args)
    
    def lint_all_configs(self, ci_mode: bool = False) -> bool:
        """
        Lint all configuration files.
        
        Args:
            ci_mode: Enable CI/CD safe mode
        
        Returns:
            True if all configs are valid, False otherwise
        """
        args = ["--lint-all"]
        
        if ci_mode:
            args.append("--ci")
        
        self.logger.info(f"Linting all configurations" + (" in CI mode" if ci_mode else ""))
        
        return self._execute(args)
    
    def plan_schema_changes(self, database_id: str) -> Any:
        """
        Plan schema changes for a database (dry run).
        
        Args:
            database_id: Database identifier in format <db_type>.<db_name>
        
        Returns:
            Result from run_sh
        """
        # Validate database identifier format
        if '.' not in database_id:
            self.logger.error(f"Invalid database ID format: {database_id}. Expected format: <db_type>.<db_name>")
            return False
        
        args = ["--plan-schema", "-d", database_id]
        
        self.logger.info(f"Planning schema changes for database: {database_id}")
        
        return self._execute(args)
    
    def apply_schema_changes(self, database_id: str) -> bool:
        """
        Apply approved schema changes to a database.
        
        Args:
            database_id: Database identifier in format <db_type>.<db_name>
        
        Returns:
            True if successful, False otherwise
        """
        # Validate database identifier format
        if '.' not in database_id:
            self.logger.error(f"Invalid database ID format: {database_id}. Expected format: <db_type>.<db_name>")
            return False
        
        args = ["--apply-schema", "-d", database_id]
        
        self.logger.info(f"Applying schema changes to database: {database_id}")
        
        return self._execute(args)

def _run_sh(args_list):
        from core.utils.scripts import run_db_mng
        return run_db_mng(args=args_list)
    
db_mng_control = _DatabaseScript(run_sh=_run_sh, verbose=True)
