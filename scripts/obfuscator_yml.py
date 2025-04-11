#!/usr/bin/env python3
"""
YAML Key Obfuscator

This utility obfuscates specified keys in YAML files by replacing them with random alphanumeric strings.
It's useful for anonymizing sensitive data structures while preserving the overall structure.

Example usage:
  Basic:
    python3 obfuscator_yml.py config.yaml metadata.users
    
  Multiple paths:
    python3 obfuscator_yml.py config.yaml metadata.users services.endpoints --output anonymized.yaml
    
  Help:
    python3 obfuscator_yml.py --help
"""
import argparse
import os
import random
import string
import yaml
import re
from copy import deepcopy

def random_alphanumeric(length=10):
    """
    Generate a random string of letters and digits.
    
    Args:
        length (int): Length of the random string to generate (default: 10)
        
    Returns:
        str: Random alphanumeric string of specified length
    
    Example:
        >>> random_alphanumeric(5)
        'a7X9c'
    """
    return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(length))

def get_nested_dict_value(d, path):
    """
    Get a value from a nested dictionary using a dot-separated path.
    
    Args:
        d (dict): The dictionary to search in
        path (str): Dot-separated path (e.g., 'config.server.ports')
        
    Returns:
        The value at the path, or None if the path doesn't exist
        
    Example:
        >>> data = {'config': {'server': {'ports': [80, 443]}}}
        >>> get_nested_dict_value(data, 'config.server.ports')
        [80, 443]
    """
    keys = path.split('.')
    current = d
    for key in keys:
        if key not in current:
            return None
        current = current[key]
    return current

def set_nested_dict_value(d, path, value):
    """
    Set a value in a nested dictionary using a dot-separated path.
    
    Args:
        d (dict): The dictionary to modify
        path (str): Dot-separated path (e.g., 'config.server.ports')
        value: The value to set at the specified path
        
    Example:
        >>> data = {'config': {'server': {}}}
        >>> set_nested_dict_value(data, 'config.server.ports', [80, 443])
        >>> data
        {'config': {'server': {'ports': [80, 443]}}}
    """
    keys = path.split('.')
    current = d
    for i, key in enumerate(keys):
        if i == len(keys) - 1:
            current[key] = value
        else:
            current = current[key]

def obfuscate_keys(data, key_path):
    """
    Obfuscate all child-level keys under the given key path.
    Only obfuscates the immediate child keys, preserving their structure.
    
    Args:
        data (dict): The dictionary containing the data to obfuscate
        key_path (str): Dot-separated path to the dictionary whose keys should be obfuscated
        
    Returns:
        tuple: (modified_data, obfuscation_map)
            - modified_data is the data with obfuscated keys
            - obfuscation_map is a dictionary mapping original keys to obfuscated keys
            
    Example:
        >>> data = {'users': {'john': {'age': 30}, 'alice': {'age': 25}}}
        >>> obfuscated, mapping = obfuscate_keys(data, 'users')
        >>> # Now 'john' and 'alice' are replaced with random strings in the data
        >>> mapping
        {'john': 'x7dF9a2Bc1', 'alice': 'pQ8sR3vZ0y'}
    """
    # Get the target dictionary to modify
    target_dict = get_nested_dict_value(data, key_path)
    if target_dict is None or not isinstance(target_dict, dict):
        print(f"Warning: Key path '{key_path}' not found or is not a dictionary.")
        return data, {}
    
    # Create a copy to avoid modifying the original during iteration
    obfuscated_dict = {}
    obfuscation_map = {}

    # Replace all keys with random alphanumeric strings
    for key in target_dict:
        new_key = random_alphanumeric(10)
        obfuscated_dict[new_key] = deepcopy(target_dict[key])
        obfuscation_map[key] = new_key
    
    # Now update the original data with our obfuscated dictionary
    set_nested_dict_value(data, key_path, obfuscated_dict)
    
    return data, obfuscation_map

def process_yaml_file(input_file, output_file, key_paths):
    """
    Process a YAML file, obfuscating the specified keys and writing to a new file.
    
    Args:
        input_file (str): Path to the input YAML file
        output_file (str): Path where the obfuscated YAML will be written
        key_paths (list): List of dot-separated paths to keys whose children should be obfuscated
        
    Example:
        >>> process_yaml_file('config.yaml', 'config.obfuscated.yaml', ['users', 'api.keys'])
        Successfully obfuscated YAML and saved to config.obfuscated.yaml
        
        Obfuscation mapping:
        
        Key path: users
          admin → j7dF9a2Bc1
          guest → pQ8sR3vZ0y
        
        Key path: api.keys
          production → x7Yt5qA3z8
          development → bN4mP2cK9d
    """
    try:
        with open(input_file, 'r') as f:
            yaml_content = yaml.safe_load(f)
        
        all_obfuscation_maps = {}
        
        # Process each key path
        for key_path in key_paths:
            yaml_content, obfuscation_map = obfuscate_keys(yaml_content, key_path)
            if obfuscation_map:  # Only add to results if we actually obfuscated something
                all_obfuscation_maps[key_path] = obfuscation_map
        
        with open(output_file, 'w') as f:
            yaml.dump(yaml_content, f, default_flow_style=False)
        
        if all_obfuscation_maps:
            print(f"Successfully obfuscated YAML and saved to {output_file}")
            print("\nObfuscation mapping:")
            for key_path, mapping in all_obfuscation_maps.items():
                print(f"\nKey path: {key_path}")
                for original, obfuscated in mapping.items():
                    print(f"  {original} → {obfuscated}")
        else:
            print("No keys were obfuscated. Check if the provided key paths exist in the YAML.")
        
    except Exception as e:
        print(f"Error processing YAML file: {e}")

def main():
    """
    Main function to parse command line arguments and call the processing function.
    
    Command-line usage examples:
    
    1. Basic usage - obfuscate a single path:
       python3 yaml_obfuscator.py config.yaml users
       
    2. Multiple paths:
       python3 yaml_obfuscator.py config.yaml users.admins services.endpoints
       
    3. Specify output file:
       python3 yaml_obfuscator.py config.yaml users --output anonymized_config.yaml
       
    4. Deeply nested paths:
       python3 yaml_obfuscator.py complex.yaml data.metadata.users.personal
    """
    parser = argparse.ArgumentParser(
        description='Obfuscate keys in YAML files while preserving structure.',
        epilog="""
Examples:
  python3 yaml_obfuscator.py config.yaml users
    Obfuscates all keys under the 'users' section and saves to config.obfuscated.yaml
    
  python3 yaml_obfuscator.py config.yaml users.admins services.endpoints -o anon.yaml
    Obfuscates keys under 'users.admins' and 'services.endpoints', saving to anon.yaml
    
  python3 yaml_obfuscator.py app_config.yaml database.credentials
    Obfuscates database credential keys, useful for sharing configs without exposing sensitive data
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument('input_file', help='Input YAML file path')
    parser.add_argument('key_paths', nargs='+', help='One or more dot-separated paths to keys whose children should be obfuscated')
    parser.add_argument('--output', '-o', help='Output file path (default: input_file with .obfuscated.yaml suffix)')
    
    args = parser.parse_args()
    
    if not os.path.exists(args.input_file):
        print(f"Error: Input file '{args.input_file}' not found.")
        return
    
    if args.output:
        output_file = args.output
    else:
        base, ext = os.path.splitext(args.input_file)
        output_file = f"{base}.obfuscated{ext}"
    
    process_yaml_file(args.input_file, output_file, args.key_paths)

if __name__ == "__main__":
    main()