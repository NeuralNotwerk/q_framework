#!/usr/bin/env python3

"""
build_framework_installer.py
Scans existing .amazonq folder and generates install_q_framework.sh with all content
"""

import argparse
import os
import sys
import base64
import shlex
from pathlib import Path
import stat

def show_help():
    """Display comprehensive help information"""
    help_text = """
Build Framework Generator

USAGE:
    python3 build_framework_installer.py [PATH]
    ./build_framework_installer.py [OPTIONS] [PATH]

DESCRIPTION:
    Scans specified files and directories (including .amazonq folder by default)
    and generates a complete install_q_framework.sh script that recreates the
    entire structure with all content.

ARGUMENTS:
    PATH                    Source directory to scan (default: current directory)

OPTIONS:
    -h, --help             Show this help message
    -o, --output FILE      Specify output filename (default: install_q_framework.sh)
    -f, --force            Overwrite existing script without confirmation
    -v, --verbose          Enable verbose output during generation
    --no-exec              Don't make the generated script executable
    --include PATH         Add file/directory to include (can be used multiple times)
    --exclude PATH         Add file/directory to exclude (can be used multiple times)
    --clear-defaults       Clear default includes (.amazonq, AmazonQ.md)

DEFAULT INCLUDES:
    .amazonq/              Complete AmazonQ folder structure
    AmazonQ.md             Main documentation file

OPERATION TYPE:
    Read-only: NO - This script creates files
    Mutating: YES - Creates/overwrites shell script files

EXAMPLES:
    python3 build_framework_installer.py                           # Default: include .amazonq/ and AmazonQ.md
    python3 build_framework_installer.py --include config.yaml     # Add config.yaml to defaults
    python3 build_framework_installer.py --exclude .amazonq/temp   # Exclude temp folder
    python3 build_framework_installer.py --clear-defaults --include .amazonq  # Only .amazonq, no AmazonQ.md
    python3 build_framework_installer.py --include "*.md"          # Include all markdown files
    python3 build_framework_installer.py --exclude "*.log" -v      # Exclude logs with verbose output

EXCLUSION PATTERNS:
    - Exact matches: --exclude .amazonq/temp
    - Wildcards: --exclude "*.log" --exclude "temp/*"
    - Directories: --exclude node_modules

REQUIREMENTS:
    - At least one included path must exist in source directory
    - Included paths should contain relevant AmazonQ content

OUTPUT:
    Creates install_q_framework.sh containing all scanned content and structure.
    The generated script will recreate the complete environment.
"""
    print(help_text)

def escape_shell_content(content):
    """Escape content for safe embedding in shell script"""
    # Use base64 encoding for complete safety with any content
    encoded = base64.b64encode(content.encode('utf-8')).decode('ascii')
    return encoded

def is_binary_file(filepath):
    """Check if file appears to be binary"""
    try:
        with open(filepath, 'rb') as f:
            chunk = f.read(1024)
            return b'\0' in chunk
    except:
        return True

def matches_pattern(path_str, pattern):
    """Check if path matches a pattern (supports wildcards)"""
    import fnmatch
    return fnmatch.fnmatch(path_str, pattern) or fnmatch.fnmatch(str(Path(path_str).name), pattern)

def should_exclude(path, exclude_patterns, verbose=False):
    """Check if path should be excluded based on patterns"""
    path_str = str(path)
    
    for pattern in exclude_patterns:
        if matches_pattern(path_str, pattern):
            if verbose:
                print(f"  → Excluding {path_str} (matches pattern: {pattern})")
            return True
    return False

def scan_paths(source_path, include_paths, exclude_patterns, verbose=False):
    """Scan specified paths and return file structure with content"""
    structure = {
        'directories': [],
        'files': []
    }
    
    def log_verbose(message):
        if verbose:
            print(f"  → {message}")
    
    processed_dirs = set()
    
    for include_path in include_paths:
        full_path = source_path / include_path
        
        if not full_path.exists():
            log_verbose(f"Include path does not exist: {include_path}")
            continue
            
        log_verbose(f"Processing include path: {include_path}")
        
        if full_path.is_file():
            # Single file
            if should_exclude(include_path, exclude_patterns, verbose):
                continue
                
            try:
                if is_binary_file(full_path):
                    log_verbose(f"Skipping binary file: {include_path}")
                    continue
                
                with open(full_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                structure['files'].append({
                    'path': include_path,
                    'content': content,
                    'size': len(content)
                })
                
                log_verbose(f"Added file: {include_path} ({len(content)} chars)")
                
            except Exception as e:
                log_verbose(f"Error reading {include_path}: {e}")
                continue
                
        elif full_path.is_dir():
            # Directory - walk recursively
            for root, dirs, files in os.walk(full_path):
                root_path = Path(root)
                
                # Get relative path from source
                try:
                    rel_path = root_path.relative_to(source_path)
                except ValueError:
                    continue
                
                # Check if directory should be excluded
                if should_exclude(rel_path, exclude_patterns, verbose):
                    dirs.clear()  # Don't recurse into excluded directories
                    continue
                
                # Add directory to structure (avoid duplicates)
                rel_path_str = str(rel_path)
                if rel_path_str not in processed_dirs:
                    structure['directories'].append(rel_path_str)
                    processed_dirs.add(rel_path_str)
                    log_verbose(f"Found directory: {rel_path_str}")
                
                # Process subdirectories
                dirs[:] = [d for d in dirs if not should_exclude(rel_path / d, exclude_patterns, verbose)]
                
                # Add files in this directory
                for filename in files:
                    file_path = root_path / filename
                    file_rel_path = rel_path / filename
                    
                    # Check if file should be excluded
                    if should_exclude(file_rel_path, exclude_patterns, verbose):
                        continue
                    
                    try:
                        if is_binary_file(file_path):
                            log_verbose(f"Skipping binary file: {file_rel_path}")
                            continue
                        
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                        
                        structure['files'].append({
                            'path': str(file_rel_path),
                            'content': content,
                            'size': len(content)
                        })
                        
                        log_verbose(f"Added file: {file_rel_path} ({len(content)} chars)")
                        
                    except Exception as e:
                        log_verbose(f"Error reading {file_rel_path}: {e}")
                        continue
    
    return structure

def generate_shell_script(structure, verbose=False):
    """Generate complete shell script from scanned structure"""
    
    script_header = '''#!/bin/bash

# install_q_framework.sh
# Recreates complete AmazonQ folder structure with all content
# Generated by build_framework_installer.py

# Colors for output
RED='\\033[0;31m'
GREEN='\\033[0;32m'
YELLOW='\\033[1;33m'
BLUE='\\033[0;34m'
NC='\\033[0m' # No Color

# Function to print colored output
print_status() {
    local color=$1
    local message=$2
    echo -e "${color}${message}${NC}"
}

# Function to show help
show_help() {
    cat << EOF
AmazonQ Complete Framework Setup Script

USAGE:
    $0 [OPTIONS]

DESCRIPTION:
    Recreates the complete AmazonQ agent folder structure with all
    rules, scripts, shell scripts, and memory files from the original
    source environment.

OPTIONS:
    -h, --help          Show this help message
    -f, --force         Overwrite existing files without backup
    -b, --backup-dir    Specify custom backup directory (default: .amazonq_backup_TIMESTAMP)
    -v, --verbose       Enable verbose output
    -d, --dry-run       Show what would be created without making changes

OPERATION TYPE:
    Read-only: NO - This script creates directories and files
    Mutating: YES - Modifies filesystem structure

EXAMPLES:
    $0                      # Create complete structure
    $0 -v                   # Create with verbose output
    $0 --dry-run            # Preview what would be created
    $0 -f                   # Force overwrite existing files

EOF
}

# Default values
FORCE=false
VERBOSE=false
DRY_RUN=false
BACKUP_DIR=""

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            show_help
            exit 0
            ;;
        -f|--force)
            FORCE=true
            shift
            ;;
        -v|--verbose)
            VERBOSE=true
            shift
            ;;
        -d|--dry-run)
            DRY_RUN=true
            shift
            ;;
        -b|--backup-dir)
            BACKUP_DIR="$2"
            shift 2
            ;;
        *)
            print_status $RED "Unknown option: $1"
            echo "Use -h or --help for usage information"
            exit 1
            ;;
    esac
done

# Set backup directory if not specified
if [[ -z "$BACKUP_DIR" ]]; then
    BACKUP_DIR=".amazonq_backup_$(date +%Y%m%d_%H%M%S)"
fi

# Verbose logging function
log_verbose() {
    if [[ "$VERBOSE" == true ]]; then
        print_status $BLUE "  → $1"
    fi
}

# Dry run logging function
log_dry_run() {
    if [[ "$DRY_RUN" == true ]]; then
        print_status $YELLOW "DRY RUN: $1"
    fi
}

# Function to create directory
create_directory() {
    local dir_path=$1
    
    log_dry_run "Would create directory: $dir_path"
    
    if [[ "$DRY_RUN" == false ]]; then
        if [[ ! -d "$dir_path" ]]; then
            mkdir -p "$dir_path"
            log_verbose "Created directory: $dir_path"
            print_status $GREEN "✓ Created directory: $dir_path"
        else
            log_verbose "Directory already exists: $dir_path"
            print_status $YELLOW "✓ Directory exists: $dir_path"
        fi
    fi
}

# Function to backup existing file
backup_file() {
    local file_path=$1
    local backup_path="$BACKUP_DIR/$(dirname "$file_path")"
    
    if [[ -f "$file_path" ]] && [[ "$FORCE" == false ]]; then
        log_dry_run "Would backup: $file_path → $backup_path/"
        
        if [[ "$DRY_RUN" == false ]]; then
            mkdir -p "$backup_path"
            cp "$file_path" "$backup_path/"
            log_verbose "Backed up: $file_path"
            print_status $YELLOW "✓ Backed up existing: $file_path"
        fi
        return 0
    fi
    return 1
}

# Function to create file from base64 content
create_file_from_base64() {
    local file_path=$1
    local base64_content=$2
    
    log_dry_run "Would create file: $file_path"
    
    if [[ "$DRY_RUN" == false ]]; then
        # Backup existing file if it exists and force is not set
        backup_file "$file_path"
        
        # Create directory if it doesn't exist
        mkdir -p "$(dirname "$file_path")"
        
        # Decode and create the file
        echo "$base64_content" | base64 -d > "$file_path"
        log_verbose "Created file: $file_path"
        print_status $GREEN "✓ Created file: $file_path"
    fi
}
'''

    # Add directory creation section
    directories_section = "\n# Create all directories\ncreate_directories() {\n"
    directories_section += "    print_status $BLUE \"Creating directory structure...\"\n"
    
    for directory in sorted(structure['directories']):
        directories_section += f'    create_directory "{directory}"\n'
    
    directories_section += "}\n"

    # Add file creation section
    files_section = "\n# Create all files\ncreate_files() {\n"
    files_section += "    print_status $BLUE \"Creating files...\"\n"
    
    for file_info in structure['files']:
        file_path = file_info['path']
        encoded_content = escape_shell_content(file_info['content'])
        
        files_section += f'\n    # Creating {file_path} ({file_info["size"]} chars)\n'
        files_section += f'    create_file_from_base64 "{file_path}" "{encoded_content}"\n'
    
    files_section += "}\n"

    # Add main execution section
    main_section = '''
# Main execution
main() {
    print_status $BLUE "=== AmazonQ Complete Framework Setup ==="
    
    if [[ "$DRY_RUN" == true ]]; then
        print_status $YELLOW "DRY RUN MODE - No changes will be made"
        echo ""
    fi
    
    # Create directory structure
    create_directories
    echo ""
    
    # Create all files
    create_files
    echo ""
    
    print_status $GREEN "=== Setup Complete ==="
    
    if [[ "$DRY_RUN" == false ]]; then
        echo ""
        print_status $BLUE "Complete AmazonQ structure recreated at: $(pwd)/.amazonq"
        
        if [[ -d "$BACKUP_DIR" ]]; then
            print_status $YELLOW "Existing files backed up to: $BACKUP_DIR"
        fi
        
        echo ""
        print_status $BLUE "Framework is ready for use!"
    fi
}

# Run main function
main'''

    # Combine all sections
    complete_script = script_header + directories_section + files_section + main_section
    
    if verbose:
        print(f"Generated script with {len(structure['directories'])} directories and {len(structure['files'])} files")
    
    return complete_script

def confirm_overwrite(filepath):
    """Ask user for confirmation to overwrite existing file"""
    response = input(f"File {filepath} already exists. Overwrite? (y/N): ")
    return response.lower() in ['y', 'yes']

def log_verbose(message, verbose=False):
    """Print message if verbose mode is enabled"""
    if verbose:
        print(f"  → {message}")

def main():
    """Main execution function"""
    parser = argparse.ArgumentParser(
        description="Generate complete install_q_framework.sh from existing .amazonq structure",
        add_help=False
    )
    
    parser.add_argument('path', nargs='?', default=os.getcwd(),
                       help='Source directory containing .amazonq (default: current directory)')
    parser.add_argument('-h', '--help', action='store_true',
                       help='Show help message')
    parser.add_argument('-o', '--output', default='install_q_framework.sh',
                       help='Output filename (default: install_q_framework.sh)')
    parser.add_argument('-f', '--force', action='store_true',
                       help='Overwrite existing files without confirmation')
    parser.add_argument('-v', '--verbose', action='store_true',
                       help='Enable verbose output')
    parser.add_argument('--no-exec', action='store_true',
                       help="Don't make the generated script executable")
    parser.add_argument('--include', action='append', default=['.amazonq', 'AmazonQ.md'],
                       help='Files/directories to include (default: .amazonq, AmazonQ.md)')
    parser.add_argument('--exclude', action='append', default=[],
                       help='Files/directories to exclude (can be used multiple times)')
    parser.add_argument('--clear-defaults', action='store_true',
                       help='Clear default includes, only use explicitly specified --include')
    
    args = parser.parse_args()
    
    # Handle help manually for custom formatting
    if args.help:
        show_help()
        sys.exit(0)
    
    # Handle include/exclude arguments
    if args.clear_defaults:
        include_paths = []
    else:
        include_paths = ['.amazonq', 'AmazonQ.md']
    
    if args.include:
        include_paths.extend(args.include)
    
    exclude_patterns = args.exclude if args.exclude else []
    
    # Remove duplicates while preserving order
    include_paths = list(dict.fromkeys(include_paths))
    
    # Resolve paths
    source_path = Path(args.path).resolve()
    output_file = source_path / args.output
    
    try:
        # Validate source directory
        if not source_path.exists():
            print(f"Error: Source directory {source_path} does not exist")
            sys.exit(1)
        
        if not source_path.is_dir():
            print(f"Error: {source_path} is not a directory")
            sys.exit(1)
        
        log_verbose(f"Source directory: {source_path}", args.verbose)
        log_verbose(f"Include paths: {include_paths}", args.verbose)
        log_verbose(f"Exclude patterns: {exclude_patterns}", args.verbose)
        log_verbose(f"Output file: {output_file}", args.verbose)
        
        # Check if output file exists
        if output_file.exists() and not args.force:
            if not confirm_overwrite(output_file):
                print("Operation cancelled.")
                sys.exit(0)
        
        # Scan the specified paths
        print(f"Scanning included paths...")
        structure = scan_paths(source_path, include_paths, exclude_patterns, args.verbose)
        
        print(f"Found {len(structure['directories'])} directories and {len(structure['files'])} files")
        
        if len(structure['files']) == 0:
            print("Warning: No files found to include. Check your include/exclude patterns.")
            print(f"Include paths: {include_paths}")
            print(f"Exclude patterns: {exclude_patterns}")
            
            response = input("Continue anyway? (y/N): ")
            if response.lower() not in ['y', 'yes']:
                sys.exit(0)
        
        # Generate the complete shell script
        print(f"Generating complete framework setup script...")
        script_content = generate_shell_script(structure, args.verbose)
        
        log_verbose("Writing shell script content", args.verbose)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(script_content)
        
        # Make executable unless --no-exec is specified
        if not args.no_exec:
            log_verbose("Making script executable", args.verbose)
            current_mode = output_file.stat().st_mode
            output_file.chmod(current_mode | stat.S_IEXEC)
        
        print(f"✓ Generated: {output_file}")
        
        if not args.no_exec:
            print(f"✓ Script is executable")
        
        file_size = output_file.stat().st_size
        print(f"✓ Script size: {file_size:,} bytes")
        print(f"✓ Included {len(include_paths)} path(s): {', '.join(include_paths)}")
        if exclude_patterns:
            print(f"✓ Excluded {len(exclude_patterns)} pattern(s): {', '.join(exclude_patterns)}")
        
        print(f"\nNext steps:")
        print(f"1. Copy script to target location")
        print(f"2. Run: {output_file.name}")
        print(f"3. Or with options: {output_file.name} --help")
        
    except FileNotFoundError as e:
        print(f"Error: {e}")
        print("Check that your include paths exist in the source directory")
        sys.exit(1)
    except PermissionError:
        print(f"Error: Permission denied writing to {output_file}")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()