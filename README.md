# AmazonQ Framework Generator

This project provides a framework for creating and managing an AmazonQ CLI environment. It consists of a build script that generates a shell script to recreate the entire AmazonQ folder structure and content.

## Origin/Concept

Many of the concepts in this project are a derivation of the Cline project with added flare to focus on AmazonQ CLI and its workflows and capabilities.

## Overview

The project contains two main components:

1. `build_framework_installer.py` - A Python script that scans the existing `.amazonq` directory structure and generates a shell script
2. `install_q_framework.sh` - The generated shell script that can recreate the entire AmazonQ environment

## How It Works

### Build Process

The `build_framework_installer.py` script:

1. Scans the specified directories (by default `.amazonq` and `AmazonQ.md`)
2. Captures all directory structures and file contents
3. Base64-encodes the file contents for safe embedding in a shell script
4. Generates a comprehensive shell script (`install_q_framework.sh`) that can recreate the entire structure

### Generated Script

The `install_q_framework.sh` script:

1. Creates all necessary directories
2. Recreates all files with their original content
3. Provides options for backup, dry-run, and verbose output
4. Handles error conditions gracefully

## Project Structure

```
/
├── build_framework_installer.py # The build script that generates the setup script
├── install_q_framework.sh       # The generated script that recreates the AmazonQ environment
├── AmazonQ.md                 # Main documentation file for the AmazonQ agent
└── .amazonq/                  # The AmazonQ agent directory structure
    ├── memory/                # Persistent memory files for maintaining context
    │   ├── activeContext.md   # Current working state and immediate focus
    │   ├── projectBrief.md    # Project goals and requirements
    │   ├── systemPatterns.md  # Technical architecture and design decisions
    │   ├── techContext.md     # Development environment details
    │   └── projectProgress.md # Implementation status tracking
    ├── rules/                 # Rules that must be strictly followed
    │   └── python/
    │       └── project_testing.md # Example rule for Python testing
    ├── scripts/               # Prompt-based scripts for specialized tasks
    │   ├── README.md          # Documentation for scripts directory
    │   └── user_request_decomposition.md # Example script for request analysis
    ├── shell_scripts/         # Executable automation scripts
    │   └── README.md          # Documentation for shell scripts
    └── mcp.json               # MCP (Model Context Protocol) configuration
```

## File Descriptions

### Core Files

- **build_framework_installer.py**: Python script that scans the `.amazonq` directory structure and generates `install_q_framework.sh`. It supports various command-line options for customizing the build process.

- **install_q_framework.sh**: Generated shell script that recreates the entire AmazonQ environment. It includes functions for creating directories, backing up existing files, and creating new files from base64-encoded content.

- **AmazonQ.md**: Main documentation file that defines the AmazonQ agent's behavior, capabilities, and interaction patterns.

### .amazonq Directory

#### Memory Files

These files serve as the agent's persistent knowledge base across sessions:

- **activeContext.md**: Tracks the current working state and immediate focus
- **projectBrief.md**: Defines project goals, requirements, and scope
- **systemPatterns.md**: Documents technical architecture and design decisions
- **techContext.md**: Contains development environment details and constraints
- **projectProgress.md**: Tracks implementation status and history

#### Rules Directory

Contains rules that must be strictly followed by the AmazonQ agent:

- **python/project_testing.md**: Example rule defining testing constraints for Python projects

#### Scripts Directory

Contains prompt-based scripts that extend the agent's capabilities:

- **README.md**: Documentation for the scripts directory
- **user_request_decomposition.md**: Example script for breaking down complex user requests

#### Shell Scripts Directory

Contains executable automation scripts:

- **README.md**: Documentation for shell scripts directory

## Usage

### Building the Framework

```bash
python3 build_framework_installer.py [OPTIONS] [PATH]
```

Options:
- `-h, --help`: Show help message
- `-o, --output FILE`: Specify output filename (default: install_q_framework.sh)
- `-f, --force`: Overwrite existing script without confirmation
- `-v, --verbose`: Enable verbose output during generation
- `--no-exec`: Don't make the generated script executable
- `--include PATH`: Add file/directory to include (can be used multiple times)
- `--exclude PATH`: Add file/directory to exclude (can be used multiple times)
- `--clear-defaults`: Clear default includes (.amazonq, AmazonQ.md)

### Setting Up the Framework

```bash
./install_q_framework.sh [OPTIONS]
```

Options:
- `-h, --help`: Show help message
- `-f, --force`: Overwrite existing files without backup
- `-b, --backup-dir`: Specify custom backup directory
- `-v, --verbose`: Enable verbose output
- `-d, --dry-run`: Show what would be created without making changes

## Purpose

This framework provides a structured way to:

1. Define and maintain an AmazonQ agent's behavior and capabilities
2. Preserve context across sessions through memory files
3. Enforce consistent rules and patterns
4. Extend functionality through specialized scripts
5. Package and distribute the entire environment as a single shell script

The generated `install_q_framework.sh` script can be shared and executed to recreate the exact same AmazonQ environment on any compatible system.
