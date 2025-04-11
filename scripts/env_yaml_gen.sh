#!/bin/bash
# ===============================================================
# YAML Environment Variable Extractor
# ===============================================================
# Version: 1.0.0
# Author: Claude
# Date: April 10, 2025
# 
# Description:
#   This script extracts environment variables referenced in a YAML 
#   configuration file (in the format ${VAR_NAME}) and generates a
#   .env file with placeholders for each unique variable.
#
# Usage:
#   ./extract-env.sh [-c CONFIG_FILE] [-e ENV_FILE] [-h]
#
# Options:
#   -c CONFIG_FILE    Path to the YAML configuration file (default: paste.txt)
#   -e ENV_FILE       Path to the output .env file (default: .env)
#   -h                Display this help message and exit
#
# Examples:
#   ./extract-env.sh                      # Use default filenames
#   ./extract-env.sh -c config.yaml       # Specify config file
#   ./extract-env.sh -e .env.production   # Specify env output file
#   ./extract-env.sh -c db.yaml -e .env.db  # Specify both files
# ===============================================================

VERSION="1.0.0"

# Default file paths
CONFIG_FILE="paste.txt"
ENV_FILE=".env"

# Function to display usage information
show_usage() {
    echo "Usage: $0 [-c CONFIG_FILE] [-e ENV_FILE] [-h]"
    echo ""
    echo "Options:"
    echo "  -c CONFIG_FILE    Path to the YAML configuration file (default: paste.txt)"
    echo "  -e ENV_FILE       Path to the output .env file (default: .env)"
    echo "  -h                Display this help message and exit"
    echo ""
    echo "Examples:"
    echo "  $0                      # Use default filenames"
    echo "  $0 -c config.yaml       # Specify config file"
    echo "  $0 -e .env.production   # Specify env output file"
    echo "  $0 -c db.yaml -e .env.db  # Specify both files"
}

# Function to display version information
show_version() {
    echo "YAML Environment Variable Extractor v$VERSION"
}

# Parse command line arguments
while getopts ":c:e:hv" opt; do
    case ${opt} in
        c)
            CONFIG_FILE=$OPTARG
            ;;
        e)
            ENV_FILE=$OPTARG
            ;;
        h)
            show_usage
            exit 0
            ;;
        v)
            show_version
            exit 0
            ;;
        \?)
            echo "Error: Invalid option: -$OPTARG" 1>&2
            show_usage
            exit 1
            ;;
        :)
            echo "Error: Option -$OPTARG requires an argument." 1>&2
            show_usage
            exit 1
            ;;
    esac
done

# Check if config file exists
if [ ! -f "$CONFIG_FILE" ]; then
    echo "Error: Configuration file '$CONFIG_FILE' not found!" 1>&2
    exit 1
fi

# Function to extract environment variables from the YAML file
extract_env_vars() {
    # Create or overwrite the output .env file with a header
    echo "# Auto-generated .env from $CONFIG_FILE" > "$ENV_FILE"
    echo "# Generated on $(date)" >> "$ENV_FILE"
    echo "# YAML Environment Variable Extractor v$VERSION" >> "$ENV_FILE"
    echo "" >> "$ENV_FILE"
    
    # Log start of extraction process
    echo "Extracting environment variables from '$CONFIG_FILE'..."
    
    # Find all values with ${...} pattern using grep
    # -o: Only output the matched parts
    # '\${[^}]*}': Regex pattern to match ${VARIABLE_NAME} format
    grep -o '\${[^}]*}' "$CONFIG_FILE" | sort | uniq | while read -r match; do
        # Extract variable name by removing ${ prefix and } suffix
        var_name=$(echo "$match" | sed 's/\${//;s/}//;')
        
        # Skip empty variable names (shouldn't happen, but just in case)
        if [ -z "$var_name" ]; then
            continue
        fi
        
        # Write the variable to the .env file with a REPLACE_ME prefix
        echo "$var_name=REPLACE_ME" >> "$ENV_FILE"
        
        # Uncomment to see each variable as it's extracted
        # echo "  - Found variable: $var_name"
    done
}

# Main execution starts here
echo "=== YAML Environment Variable Extractor v$VERSION ==="
echo "Config file: $CONFIG_FILE"
echo "Output .env: $ENV_FILE"
echo ""

# Call the extraction function
extract_env_vars

# Count how many variables were extracted
var_count=$(grep -c "=" "$ENV_FILE")

# Print completion message
if [ $var_count -eq 0 ]; then
    echo "⚠️  No environment variables found in $CONFIG_FILE."
else
    echo "✅ .env file created with $var_count variables."
    echo "   Please replace REPLACE_ME with real secrets."
fi

# Provide additional guidance
echo ""
echo "Next steps:"
echo "1. Review the $ENV_FILE file"
echo "2. Replace all REPLACE_ME_* values with actual secret values"
echo "3. Use the populated .env file with your application"