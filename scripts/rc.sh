#!/bin/bash

#####################################################################
# Comment Remover Script
#
# Purpose: Creates copies of code files with comments removed
#          Original files remain unchanged
#          New files named as: filename.rc.extension
#
# Supported file types:
# - JavaScript/TypeScript (.js, .ts)
# - Python (.py)
# - Dart (.dart)
# - PHP (.php)
# - Kotlin (.kt)
# - Java (.java)
# - HTML (.html)
# - CSS (.css)
# - Shell scripts (.sh)
# - Batch files (.bat)
# - YAML (.yml, .yaml)
#
# Example usage:
#   Single file:     ./comment-remover.sh script.js
#   Multiple files:  ./comment-remover.sh index.html style.css app.js
#   Directory:       ./comment-remover.sh -d src/
#
# Output:
#   Original:  script.js
#   Created:   script.rc.js  (comment-free copy)
#
#####################################################################

# Display usage if no arguments provided
if [ $# -eq 0 ]; then
  echo "Usage: $0 [file1] [file2] ..."
  echo "Or use with directory: $0 -d [directory]"
  echo ""
  echo "Examples:"
  echo "  $0 script.js                  # Process single file"
  echo "  $0 index.html style.css       # Process multiple files"
  echo "  $0 -d src/                    # Process all supported files in directory"
  exit 1
fi

# Function to remove comments based on file extension
remove_comments() {
  local input_file="$1"
  local output_file="$2"
  local extension="${input_file##*.}"
  
  echo "Processing: $input_file -> $output_file"
  
  # Handle each file type with appropriate comment removal technique
  case "$extension" in
    js|ts)
      # Remove JavaScript/TypeScript comments (both // and /* */)
      sed -E 's|//.*$||g' "$input_file" | sed -E ':a;N;$!ba;s|/\*[\s\S]*?\*/||g' > "$output_file"
      ;;
    py)
      # Remove Python comments (# and """ """)
      sed -E 's|#.*$||g' "$input_file" > "$output_file.tmp"
      python3 -c "
import sys, re
with open('$output_file.tmp', 'r') as file:
    content = file.read()
# Remove triple-quoted docstrings
content = re.sub(r'\"\"\"[\\s\\S]*?\"\"\"|\'\'\'[\\s\\S]*?\'\'\'', '', content)
with open('$output_file', 'w') as file:
    file.write(content)
" 
      rm -f "$output_file.tmp"
      ;;
    dart)
      # Remove Dart comments (// and /* */)
      sed -E 's|//.*$||g' "$input_file" | sed -E ':a;N;$!ba;s|/\*[\s\S]*?\*/||g' > "$output_file"
      ;;
    php)
      # Remove PHP comments (// and /* */ and # style)
      sed -E 's|//.*$||g' "$input_file" | sed -E 's|#.*$||g' | sed -E ':a;N;$!ba;s|/\*[\s\S]*?\*/||g' > "$output_file"
      ;;
    kt|java)
      # Remove Kotlin/Java comments (// and /* */)
      sed -E 's|//.*$||g' "$input_file" | sed -E ':a;N;$!ba;s|/\*[\s\S]*?\*/||g' > "$output_file"
      ;;
    html)
      # Remove HTML comments (<!-- -->)
      sed -E ':a;N;$!ba;s|<!--[\s\S]*?-->||g' "$input_file" > "$output_file"
      ;;
    css)
      # Remove CSS comments (/* */)
      sed -E ':a;N;$!ba;s|/\*[\s\S]*?\*/||g' "$input_file" > "$output_file"
      ;;
    sh)
      # Remove shell script comments (#)
      sed -E 's|#.*$||g' "$input_file" > "$output_file"
      ;;
    bat)
      # Remove batch file comments (REM and ::)
      sed -E 's|^[Rr][Ee][Mm].*$||g' "$input_file" | sed -E 's|^::.*$||g' > "$output_file"
      ;;
    yml|yaml)
      # Remove YAML comments (#)
      sed -E 's|#.*$||g' "$input_file" > "$output_file"
      ;;
    *)
      echo "Unsupported file type: $extension - copying without modification"
      cp "$input_file" "$output_file"
      ;;
  esac
  
  # Check if sed -i works differently on macOS vs Linux
  if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS requires an empty string argument for -i
    sed -i "" -E 's/[ \t]+$//g' "$output_file"  # Remove trailing whitespace
    sed -i "" -E '/^$/d' "$output_file"         # Remove empty lines
  else
    # Linux version
    sed -i -E 's/[ \t]+$//g' "$output_file"     # Remove trailing whitespace
    sed -i -E '/^$/d' "$output_file"            # Remove empty lines
  fi
}

# Process directory if -d flag is provided
if [ "$1" = "-d" ]; then
  # Check if directory parameter is provided and valid
  if [ -z "$2" ]; then
    echo "Error: No directory specified"
    exit 1
  fi
  
  if [ ! -d "$2" ]; then
    echo "Error: '$2' is not a directory"
    exit 1
  fi
  
  echo "Processing all supported files in directory: $2"
  
  # Find supported files and process them
  find "$2" -type f \( -name "*.js" -o -name "*.ts" -o -name "*.py" -o -name "*.dart" \
    -o -name "*.php" -o -name "*.kt" -o -name "*.java" -o -name "*.html" \
    -o -name "*.css" -o -name "*.sh" -o -name "*.bat" -o -name "*.yml" -o -name "*.yaml" \) | while read file; do
    
    # Get directory path and filename
    dir_path=$(dirname "$file")
    filename=$(basename "$file")
    extension="${filename##*.}"
    base="${filename%.*}"
    
    # Create output filename with the ".rc" pattern before extension
    output_file="$dir_path/${base}.rc.$extension"
    
    # Process the file
    remove_comments "$file" "$output_file"
  done
  
  echo "Done! Comment-free copies created with '.rc' suffix"
else
  # Process individual files
  for file in "$@"; do
    # Check if file exists
    if [ ! -f "$file" ]; then
      echo "Error: '$file' is not a file or doesn't exist"
      continue
    fi
    
    # Get directory path and filename
    dir_path=$(dirname "$file")
    filename=$(basename "$file")
    extension="${filename##*.}"
    base="${filename%.*}"
    
    # Create output filename with the ".rc" pattern
    output_file="$dir_path/${base}.rc.$extension"
    
    # Process the file
    remove_comments "$file" "$output_file"
  done
  
  echo "Done! Comment-free copies created with '.rc' suffix"
fi