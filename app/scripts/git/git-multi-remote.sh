#!/bin/bash
#
# git-multi-remote - Enhanced Git versioning system setup script
#
# Usage: ./git-multi-remote.sh [OPTIONS]
#
# Description:
#   This script provides an enhanced Git setup with multiple remote repositories,
#   git-flow pattern initialization, submodules setup, and proper initial configurations.
#
# Options:
#   -p URL      Set public remote URL (primary)
#   -P URL      Set private remote URL
#   -e URL      Set extra remote URL (can be used multiple times)
#   -n NAME     Set extra remote name (must correspond with -e, can be used multiple times)
#   -d PATH     Set directory for repository (defaults to current directory)
#   -s URL[:PATH]  Add submodule URL with optional path (can be used multiple times)
#   -i TYPE     Set gitignore template (node, python, java, etc.)
#   -m MSG      Set initial commit message (defaults to "Initial commit")
#   -r NAME     Set release branch prefix (defaults to "release")
#   -f NAME     Set feature branch prefix (defaults to "feature")
#   -h NAME     Set hotfix branch prefix (defaults to "hotfix")
#   -v          Enable verbose output
#   -?          Display this help message
#
# Examples:
#   # Basic setup with public and private remotes
#   ./git-multi-remote.sh -p https://github.com/user/repo.git -P https://private.git/user/repo.git
#
#   # Setup with python gitignore and custom commit message
#   ./git-multi-remote.sh -p https://github.com/user/repo.git -i python -m "Project foundation"
#
#   # Setup with multiple remotes and submodules
#   ./git-multi-remote.sh -p https://github.com/user/repo.git \
#       -e https://gitlab.com/user/repo.git -n gitlab \
#       -s https://github.com/user/lib.git:lib \
#       -i node -v
#
#   # Complete setup with all options
#   ./git-multi-remote.sh -d ~/projects/project \
#       -p https://github.com/user/repo.git \
#       -P https://private.git/user/repo.git \
#       -e https://gitlab.com/user/repo.git -n gitlab \
#       -e https://bitbucket.org/user/repo.git -n bitbucket \
#       -s https://github.com/user/lib1.git:lib/core \
#       -s https://github.com/user/lib2.git:lib/utils \
#       -i python -m "Initial project structure" \
#       -r rel -f feat -h fix -v
#
# Version: 1.0

# Set default values
VERBOSE=false
PROJECT_DIR="."
INIT_COMMIT_MSG="Initial commit"
FEATURE_PREFIX="feature"
RELEASE_PREFIX="release"
HOTFIX_PREFIX="hotfix"

# Arrays for storing multiple values
declare -a EXTRA_REMOTE_URLS
declare -a EXTRA_REMOTE_NAMES
declare -a SUBMODULE_SPECS

# Function to log messages if verbose mode is enabled
log() {
    if [ "$VERBOSE" = true ]; then
        echo "🔹 $1"
    fi
}

# Function to log errors
error() {
    echo "❌ ERROR: $1" >&2
}

# Function to log success
success() {
    echo "✅ $1"
}

# Display usage information
show_usage() {
    sed -n '/^# Usage:/,/^# Author:/p' "$0" | sed 's/^# //'
    exit 1
}

# Function to process command-line arguments
process_args() {
    local extra_remote_index=0
    
    while getopts "p:P:e:n:d:s:i:m:r:f:h:v?" opt; do
        case $opt in
            p) PUBLIC_REMOTE_URL="$OPTARG" ;;
            P) PRIVATE_REMOTE_URL="$OPTARG" ;;
            e) EXTRA_REMOTE_URLS+=("$OPTARG") ;;
            n) EXTRA_REMOTE_NAMES+=("$OPTARG") ;;
            d) PROJECT_DIR="$OPTARG" ;;
            s) SUBMODULE_SPECS+=("$OPTARG") ;;
            i) GITIGNORE_TYPE="$OPTARG" ;;
            m) INIT_COMMIT_MSG="$OPTARG" ;;
            r) RELEASE_PREFIX="$OPTARG" ;;
            f) FEATURE_PREFIX="$OPTARG" ;;
            h) HOTFIX_PREFIX="$OPTARG" ;;
            v) VERBOSE=true ;;
            ?) show_usage ;;
        esac
    done

    # Validate required parameters
    if [ -z "$PUBLIC_REMOTE_URL" ]; then
        error "Public remote URL (-p) is required"
        show_usage
    fi

    # Validate that extra remotes have corresponding names
    if [ ${#EXTRA_REMOTE_URLS[@]} -ne ${#EXTRA_REMOTE_NAMES[@]} ]; then
        error "Each extra remote URL (-e) must have a corresponding name (-n)"
        show_usage
    fi
}

# Create and initialize repository
initialize_repository() {
    log "Creating repository in $PROJECT_DIR"
    
    # Create directory if it doesn't exist
    mkdir -p "$PROJECT_DIR"
    cd "$PROJECT_DIR" || { error "Failed to change to directory $PROJECT_DIR"; exit 1; }
    
    # Initialize git repository
    git init || { error "Failed to initialize git repository"; exit 1; }
    success "Git repository initialized"
}

# Configure remotes
configure_remotes() {
    # Add public remote
    log "Adding public remote (origin): $PUBLIC_REMOTE_URL"
    git remote add origin "$PUBLIC_REMOTE_URL" || { error "Failed to add public remote"; exit 1; }
    
    # Add private remote if specified
    if [ -n "$PRIVATE_REMOTE_URL" ]; then
        log "Adding private remote: $PRIVATE_REMOTE_URL"
        git remote add private "$PRIVATE_REMOTE_URL" || { error "Failed to add private remote"; exit 1; }
    fi
    
    # Add extra remotes if specified
    for i in "${!EXTRA_REMOTE_URLS[@]}"; do
        log "Adding extra remote (${EXTRA_REMOTE_NAMES[$i]}): ${EXTRA_REMOTE_URLS[$i]}"
        git remote add "${EXTRA_REMOTE_NAMES[$i]}" "${EXTRA_REMOTE_URLS[$i]}" || { 
            error "Failed to add extra remote ${EXTRA_REMOTE_NAMES[$i]}"; 
            exit 1; 
        }
    done
    
    success "Remote repositories configured"
}

# Rename master branch to main
rename_main_branch() {
    log "Renaming master branch to main"
    
    # Check if branch exists (for new repos, it doesn't)
    if git show-ref --quiet refs/heads/master; then
        git branch -m master main || { error "Failed to rename master branch"; exit 1; }
    else
        # For a new repo, create an initial commit then rename
        log "No master branch found, creating main branch directly"
        echo "# Placeholder" > README.md
        git add README.md
        git commit -m "Initial placeholder" || { error "Failed to create initial commit"; exit 1; }
        git branch -m main || { error "Failed to rename branch to main"; exit 1; }
    fi
    
    success "Main branch renamed/created"
}

# Create gitignore file
create_gitignore() {
    log "Creating .gitignore file"
    
    # Base gitignore content for all projects
    cat > .gitignore << EOL
# Operating System Files
.DS_Store
Thumbs.db
*~
._*
.Spotlight-V100
.Trashes

# IDE Files
.idea/
.vscode/
*.sublime-*
.project
.settings/
.classpath
*.swp
*.swo

# Log Files
*.log
logs/
EOL

    # Add template-specific content based on project type
    if [ -n "$GITIGNORE_TYPE" ]; then
        log "Adding $GITIGNORE_TYPE specific patterns to .gitignore"
        
        case "$GITIGNORE_TYPE" in
            python)
                cat >> .gitignore << EOL

# Python specific
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib64/
parts/
sdist/
var/
*.egg-info/
.installed.cfg
*.egg
venv/
ENV/
.pytest_cache/
.coverage
htmlcov/
EOL
                ;;
                
            node)
                cat >> .gitignore << EOL

# Node.js specific
node_modules/
npm-debug.log*
yarn-debug.log*
yarn-error.log*
.npm
.yarn-integrity
coverage/
.nyc_output
.env
.env.test
.env.local
.env.development.local
.env.test.local
.env.production.local
EOL
                ;;
                
            java)
                cat >> .gitignore << EOL

# Java specific
*.class
*.jar
*.war
*.ear
*.nar
hs_err_pid*
target/
.mvn/
!**/src/main/**
!**/src/test/**
EOL
                ;;
                
            *)
                log "Unknown gitignore template: $GITIGNORE_TYPE, using default only"
                ;;
        esac
    fi
    
    git add .gitignore || { error "Failed to add .gitignore file"; exit 1; }
    success "Gitignore file created and added"
}

# Initialize git flow
initialize_git_flow() {
    log "Initializing git flow pattern"
    
    # Create develop branch
    git checkout -b develop main || { error "Failed to create develop branch"; exit 1; }
    
    # Create the initial structure for git flow branches
    mkdir -p .git/refs/heads/$FEATURE_PREFIX
    mkdir -p .git/refs/heads/$RELEASE_PREFIX
    mkdir -p .git/refs/heads/$HOTFIX_PREFIX
    
    # Create a config file for git flow
    git config --local gitflow.branch.master main
    git config --local gitflow.branch.develop develop
    git config --local gitflow.prefix.feature "$FEATURE_PREFIX/"
    git config --local gitflow.prefix.release "$RELEASE_PREFIX/"
    git config --local gitflow.prefix.hotfix "$HOTFIX_PREFIX/"
    
    success "Git flow pattern initialized"
}

# Initialize submodules
initialize_submodules() {
    if [ ${#SUBMODULE_SPECS[@]} -gt 0 ]; then
        log "Initializing ${#SUBMODULE_SPECS[@]} submodules"
        
        for spec in "${SUBMODULE_SPECS[@]}"; do
            # Parse URL and path from spec (URL:PATH format)
            IFS=':' read -r url path <<< "$spec"
            
            # If no path specified, use default (last part of URL without .git)
            if [ -z "$path" ]; then
                path=$(basename "$url" .git)
            fi
            
            log "Adding submodule: $url at path $path"
            git submodule add "$url" "$path" || { 
                error "Failed to add submodule $url"; 
                exit 1; 
            }
        done
        
        # Initialize all submodules
        git submodule update --init --recursive || { 
            error "Failed to initialize submodules"; 
            exit 1; 
        }
        
        success "Submodules initialized"
    else
        log "No submodules specified, skipping"
    fi
}

# Create initial project structure and commit
create_initial_commit() {
    log "Creating initial project structure"
    
    # Create README.md if it doesn't exist
    if [ ! -f README.md ]; then
        project_name=$(basename "$(pwd)")
        cat > README.md << EOL
# $project_name

## Description
A brief description of the project.

## Setup
Instructions for setting up the project.

## Usage
Instructions for using the project.

## License
License information.
EOL
    fi
    
    # Add all files
    git add . || { error "Failed to add files"; exit 1; }
    
    # Commit
    git commit -m "$INIT_COMMIT_MSG" || { error "Failed to create initial commit"; exit 1; }
    
    success "Initial commit created"
}

# Main execution flow
main() {
    log "Starting git-multi-remote setup"
    
    # Process command-line arguments
    process_args "$@"
    
    # Initialize repository
    initialize_repository
    
    # Rename main branch
    rename_main_branch
    
    # Create gitignore file
    create_gitignore
    
    # Initialize git flow
    initialize_git_flow
    
    # Initialize submodules
    initialize_submodules
    
    # Create initial commit
    create_initial_commit
    
    # Configure remotes
    configure_remotes
    
    success "Setup complete! Repository is ready for use."
    log "Main branch: main"
    log "Development branch: develop"
    log "Current branch: $(git branch --show-current)"
    
    # Display configured remotes
    echo
    echo "Configured remotes:"
    git remote -v
}

# Execute main function with all arguments
main "$@"