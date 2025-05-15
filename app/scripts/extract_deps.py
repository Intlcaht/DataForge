import os
import re
import argparse

# Define regex patterns for different languages
IMPORT_PATTERNS = {
    'python': r'^\s*(import|from)\s+([\w\d_\.]+)',
    'react': r'^\s*import\s+[\w\d_\*\{\}\s,]+from\s+[\'"]([@\w\d_\-\/]+)[\'"]',
    'node': r'^\s*(require|import)\([\'"]([@\w\d_\-\/]+)[\'"]',
    'go': r'^\s*import\s+[\'"]([\w\d_\-\/\.]+)[\'"]',
    'dart': r'^\s*import\s+[\'"](package:[\w\d_\-\/]+)[\'"]',
    'kotlin': r'^\s*import\s+([\w\d_\.]+)',
    'java': r'^\s*import\s+([\w\d_\.]+);',
    'laravel': r'^\s*use\s+([\w\d_\\]+);'
}

# Define file extensions for different languages
EXTENSIONS = {
    'python': ('.py',),
    'react': ('.js', '.jsx', '.ts', '.tsx'),
    'node': ('.js', '.ts'),
    'go': ('.go',),
    'dart': ('.dart',),
    'kotlin': ('.kt',),
    'java': ('.java',),
    'laravel': ('.php',)
}

def extract_dependencies(file_path, language, exclude_patterns=None):
    dependencies = set()
    if exclude_patterns is None:
        exclude_patterns = []

    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()
    except Exception as e:
        print(f"Error reading file {file_path}: {e}")
        return dependencies

    pattern = IMPORT_PATTERNS.get(language)
    if not pattern:
        raise ValueError(f"Unsupported language: {language}")

    for line in lines:
        match = re.match(pattern, line)
        if match:
            dependency = match.group(2 if language in ['python', 'node'] else 1)
            if not any(re.match(exclude, dependency) for exclude in exclude_patterns):
                dependencies.add(dependency)

    return dependencies

def scan_directory(directory, language, exclude_patterns=None):
    all_dependencies = set()
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(EXTENSIONS.get(language, '')):
                file_path = os.path.join(root, file)
                print(f"Scanning file: {file_path}")
                dependencies = extract_dependencies(file_path, language, exclude_patterns)
                all_dependencies.update(dependencies)
    return all_dependencies

def main():
    parser = argparse.ArgumentParser(description='Extract dependencies from project files.')
    parser.add_argument('directory', help='The directory to scan for dependencies.')
    parser.add_argument('language', choices=IMPORT_PATTERNS.keys(), help='The language of the project.')
    parser.add_argument('--exclude', nargs='*', help='Regex patterns to exclude internal or relative imports.')

    args = parser.parse_args()

    dependencies = scan_directory(args.directory, args.language, args.exclude)
    if dependencies:
        print("Extracted dependencies:")
        for dependency in sorted(dependencies):
            print(dependency)
    else:
        print("No dependencies found.")

if __name__ == '__main__':
    main()
