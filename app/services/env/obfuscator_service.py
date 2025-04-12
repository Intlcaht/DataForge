"""
Environment File Obfuscator Module

This module provides a Python interface for obfuscating and deobfuscating environment files (.env).
It wraps the functionality of the obfuscator_env.py script in an easy-to-use class with
comprehensive documentation, type hints, and error handling.
"""

import logging
from typing import Dict, Any, Optional, Union, List, Callable
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("EnvObfuscator")


class _EnvObfuscator:
    """
    A Python class to interact with the obfuscator_env.py script for secure handling of
    environment variables in configuration files.
    
    This class allows you to:
    - Obfuscate .env files to protect sensitive information
    - Deobfuscate previously obfuscated files using the original password and mapping file
    - Customize input/output file paths
    
    The obfuscation uses a password-based approach to secure the environment variables
    while generating a mapping file to allow for later deobfuscation.
    """
    
    def __init__(self, run_script_func: Callable[[List[str]], Any]):
        """
        Initialize the EnvObfuscator with a function to execute the underlying script.
        
        Args:
            run_script_func: A callable that accepts a list of command arguments and
                             executes the obfuscator_env.py script. This function should
                             handle the actual command execution and return the results.
        """
        self._run_script = run_script_func
        logger.info("EnvObfuscator initialized")
    
    def obfuscate(self, 
                  input_file: Union[str, Path], 
                  password: str,
                  output_file: Optional[Union[str, Path]] = None) -> Dict[str, Any]:
        """
        Obfuscate an environment file to protect sensitive information.
        
        This method takes an input .env file and encrypts its contents using the provided password.
        It also generates a mapping file that can be used later for deobfuscation.
        
        Args:
            input_file: Path to the environment file to obfuscate.
            password: Secret password used for the obfuscation process.
            output_file: Optional custom path for the obfuscated output file.
                         If not provided, the default naming convention will be used
                         (typically input_file + ".obfuscated").
        
        Returns:
            Dictionary containing the results of the obfuscation operation, including
            paths to the generated files.
            
        Raises:
            FileNotFoundError: If the input file doesn't exist.
            ValueError: If the password is empty.
            RuntimeError: If the obfuscation process fails.
        """
        # Validate inputs
        input_path = Path(input_file)
        if not input_path.exists():
            error_msg = f"Input file not found: {input_path}"
            logger.error(error_msg)
            raise FileNotFoundError(error_msg)
            
        if not password:
            error_msg = "Password cannot be empty"
            logger.error(error_msg)
            raise ValueError(error_msg)
        
        # Construct command arguments
        args = ["-i", str(input_path), "-p", password]
        
        if output_file:
            output_path = Path(output_file)
            args.extend(["-o", str(output_path)])
            logger.info(f"Obfuscating {input_path} to custom output {output_path}")
        else:
            logger.info(f"Obfuscating {input_path} with default output naming")
        
        # Execute the command
        result = self._run_script(args)
        logger.info("Obfuscation completed successfully")
        return result
    
    def deobfuscate(self,
                    input_file: Union[str, Path],
                    mapping_file: Union[str, Path],
                    password: str,
                    output_file: Optional[Union[str, Path]] = None) -> Dict[str, Any]:
        """
        Deobfuscate a previously obfuscated environment file.
        
        This method takes an obfuscated file and its corresponding mapping file,
        along with the original password, to restore the original environment variables.
        
        Args:
            input_file: Path to the obfuscated environment file.
            mapping_file: Path to the mapping file generated during obfuscation.
            password: The same secret password used during the obfuscation process.
            output_file: Optional custom path for the deobfuscated output file.
                         If not provided, the default naming convention will be used.
        
        Returns:
            Dictionary containing the results of the deobfuscation operation.
            
        Raises:
            FileNotFoundError: If the input file or mapping file doesn't exist.
            ValueError: If the password is empty.
            RuntimeError: If the deobfuscation process fails.
        """
        # Validate inputs
        input_path = Path(input_file)
        mapping_path = Path(mapping_file)
        
        if not input_path.exists():
            error_msg = f"Obfuscated input file not found: {input_path}"
            logger.error(error_msg)
            raise FileNotFoundError(error_msg)
            
        if not mapping_path.exists():
            error_msg = f"Mapping file not found: {mapping_path}"
            logger.error(error_msg)
            raise FileNotFoundError(error_msg)
            
        if not password:
            error_msg = "Password cannot be empty"
            logger.error(error_msg)
            raise ValueError(error_msg)
        
        # Construct command arguments
        args = [
            "-i", str(input_path),
            "-m", str(mapping_path),
            "-p", password,
            "-d"  # Deobfuscation flag
        ]
        
        if output_file:
            output_path = Path(output_file)
            args.extend(["-o", str(output_path)])
            logger.info(f"Deobfuscating {input_path} to custom output {output_path}")
        else:
            logger.info(f"Deobfuscating {input_path} with default output naming")
        
        # Execute the command
        result = self._run_script(args)
        logger.info("Deobfuscation completed successfully")
        return result
    
    def validate_files(self, 
                       env_file: Union[str, Path], 
                       mapping_file: Optional[Union[str, Path]] = None) -> bool:
        """
        Validate that the required files exist for obfuscation or deobfuscation.
        
        Args:
            env_file: Path to the environment file (.env or .env.obfuscated).
            mapping_file: Optional path to the mapping file (required for deobfuscation).
            
        Returns:
            True if all required files exist, False otherwise.
        """
        env_path = Path(env_file)
        
        if not env_path.exists():
            logger.warning(f"Environment file not found: {env_path}")
            return False
            
        if mapping_file:
            mapping_path = Path(mapping_file)
            if not mapping_path.exists():
                logger.warning(f"Mapping file not found: {mapping_path}")
                return False
                
        return True
    
    def get_default_output_path(self, 
                                input_path: Union[str, Path], 
                                is_deobfuscation: bool = False) -> Path:
        """
        Generate the default output path based on the input path and operation type.
        
        Args:
            input_path: The input file path.
            is_deobfuscation: Whether this is for a deobfuscation operation.
            
        Returns:
            The default output path that would be used if no custom output is specified.
        """
        path = Path(input_path)
        
        if is_deobfuscation:
            # For deobfuscation, typically removes the .obfuscated suffix if present
            if path.name.endswith('.obfuscated'):
                return path.with_name(path.stem)
            else:
                return path.with_name(f"{path.name}.deobfuscated")
        else:
            # For obfuscation, typically adds .obfuscated suffix
            return path.with_name(f"{path.name}.obfuscated")
    
    def get_default_mapping_path(self, obfuscated_file: Union[str, Path]) -> Path:
        """
        Generate the default mapping file path based on the obfuscated file path.
        
        Args:
            obfuscated_file: Path to the obfuscated file.
            
        Returns:
            The default mapping file path that would be generated during obfuscation.
        """
        path = Path(obfuscated_file)
        return path.with_name(f"{path.name}.mapping.json")

def _run_function(args: List[str]) -> Dict[str, Any]:
        """Example implementation of a function to run the obfuscator_env.py script."""
        from core.utils.scripts import  run_obfuscator_env
        return run_obfuscator_env(args=args)        

env_obfuscator = _EnvObfuscator(_run_function)

    