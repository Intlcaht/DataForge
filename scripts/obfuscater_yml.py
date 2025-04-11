#!/usr/bin/env python3
import argparse
import os
import random
import string
import yaml
import re
from copy import deepcopy

def random_alphanumeric(length=10):
    """Generate a random string of letters and digits."""
    return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(length))

def get_nested_dict_value(d, path):
    """Get a value from a nested dictionary using a dot-separated path."""
    keys = path.split('.')
    current = d
    for key in keys:
        if key not in current:
            return None
        current = current[key]
    return current

def obfuscate_keys(data, key_path):
    """
    Obfuscate all child-level keys under the given key path.
    Only obfuscates the immediate child keys, preserving their structure.
    """
    # Get the target dictionary to modify
    target_dict = get_nested_dict_value(data, key_path)
    if target_dict is None or not isinstance(target_dict, dict):
        print(f"Error: Key path '{key_path}' not found or is not a dictionary.")
        return data
    
    # Create a copy to avoid modifying the original during iteration
    obfuscated_dict = {}
    obfuscation_map = {}

    # Replace all keys with random alphanumeric strings
    for key in target_dict:
        new_key = random_alphanumeric(10)
        obfuscated_dict[new_key] = deepcopy(target_dict[key])
        obfuscation_map[key] = new_key
    
    # Now update the original data with our obfuscated dictionary
    current = data
    keys = key_path.split('.')
    for i, key in enumerate(keys):
        if i == len(keys) - 1:
            current[key] = obfuscated_dict
        else:
            current = current[key]
    
    return data, obfuscation_map

def process_yaml_file(input_file, output_file, key_path):
    """Process a YAML file, obfuscating the specified keys and writing to a new file."""
    try:
        with open(input_file, 'r') as f:
            yaml_content = yaml.safe_load(f)
        
        obfuscated_yaml, obfuscation_map = obfuscate_keys(yaml_content, key_path)
        
        with open(output_file, 'w') as f:
            yaml.dump(obfuscated_yaml, f, default_flow_style=False)
        
        print(f"Successfully obfuscated YAML and saved to {output_file}")
        print("\nObfuscation mapping:")
        for original, obfuscated in obfuscation_map.items():
            print(f"  {original} → {obfuscated}")
        
    except Exception as e:
        print(f"Error processing YAML file: {e}")

def main():
    parser = argparse.ArgumentParser(description='Obfuscate keys in YAML files.')
    parser.add_argument('input_file', help='Input YAML file path')
    parser.add_argument('key_path', help='Dot-separated path to the key whose children should be obfuscated')
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
    
    process_yaml_file(args.input_file, output_file, args.key_path)

if __name__ == "__main__":
    main()