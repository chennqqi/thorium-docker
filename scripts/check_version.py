#!/usr/bin/env python3
"""
Script to check for latest Thorium version and trigger build if needed.
Supports multiple instruction sets: AVX2, AVX, SSE3, SSE4
"""

import json
import requests
import sys
import os
from datetime import datetime

# Supported instruction sets
SUPPORTED_INSTRUCTION_SETS = ['AVX2', 'AVX', 'SSE3', 'SSE4']

def get_latest_thorium_version():
    """
    Get the latest Thorium version from GitHub releases.
    
    Returns:
        str: Latest version tag
    """
    try:
        url = "https://api.github.com/repos/Alex313031/thorium/releases/latest"
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        release_data = response.json()
        latest_version = release_data['tag_name']
        
        print(f"Latest Thorium version: {latest_version}")
        return latest_version
        
    except requests.RequestException as e:
        print(f"Error fetching latest version: {e}")
        return None
    except KeyError as e:
        print(f"Error parsing release data: {e}")
        return None

def check_docker_image_exists(image_name, version, instruction_set):
    """
    Check if Docker image with specific version and instruction set already exists.
    
    Args:
        image_name (str): Docker image name
        version (str): Version to check
        instruction_set (str): Instruction set to check
        
    Returns:
        bool: True if image exists, False otherwise
    """
    try:
        # Use Docker Hub API to check if image exists
        tag = f"{version}-{instruction_set}"
        url = f"https://hub.docker.com/v2/repositories/{image_name}/tags/{tag}/"
        response = requests.get(url, timeout=30)
        
        if response.status_code == 200:
            print(f"Image {image_name}:{tag} already exists")
            return True
        else:
            print(f"Image {image_name}:{tag} does not exist")
            return False
            
    except requests.RequestException as e:
        print(f"Error checking Docker image: {e}")
        return False

def get_instruction_sets_to_build():
    """
    Get instruction sets to build from environment or default to all.
    
    Returns:
        list: List of instruction sets to build
    """
    # Check if specific instruction set is requested
    instruction_set = os.environ.get('INSTRUCTION_SET', '').strip()
    
    if instruction_set and instruction_set.upper() in SUPPORTED_INSTRUCTION_SETS:
        return [instruction_set.upper()]
    elif instruction_set and instruction_set.lower() == 'all':
        return SUPPORTED_INSTRUCTION_SETS
    else:
        # Default to all instruction sets
        return SUPPORTED_INSTRUCTION_SETS

def check_all_instruction_sets(image_name, version, instruction_sets):
    """
    Check if all instruction set versions exist.
    
    Args:
        image_name (str): Docker image name
        version (str): Version to check
        instruction_sets (list): List of instruction sets to check
        
    Returns:
        tuple: (should_build, missing_sets)
    """
    missing_sets = []
    
    for instruction_set in instruction_sets:
        if not check_docker_image_exists(image_name, version, instruction_set):
            missing_sets.append(instruction_set)
    
    should_build = len(missing_sets) > 0
    return should_build, missing_sets

def main():
    """
    Main function to check version and determine if build is needed.
    """
    # Get repository name from environment
    repo_name = os.environ.get('GITHUB_REPOSITORY', 'chennqqi/thorium-docker')
    
    # Get latest version
    latest_version = get_latest_thorium_version()
    if not latest_version:
        print("Failed to get latest version")
        sys.exit(1)
    
    # Get instruction sets to build
    instruction_sets = get_instruction_sets_to_build()
    print(f"Checking instruction sets: {', '.join(instruction_sets)}")
    
    # Check if images already exist
    should_build, missing_sets = check_all_instruction_sets(repo_name, latest_version, instruction_sets)
    
    # Output results for GitHub Actions
    print(f"::set-output name=latest_version::{latest_version}")
    print(f"::set-output name=should_build::{should_build}")
    print(f"::set-output name=instruction_sets::{','.join(instruction_sets)}")
    
    if missing_sets:
        print(f"::set-output name=missing_sets::{','.join(missing_sets)}")
    
    # Create version info file
    version_info = {
        'latest_version': latest_version,
        'should_build': should_build,
        'instruction_sets': instruction_sets,
        'missing_sets': missing_sets,
        'checked_at': datetime.utcnow().isoformat(),
        'repository': repo_name
    }
    
    with open('version_info.json', 'w') as f:
        json.dump(version_info, f, indent=2)
    
    print(f"Version info saved to version_info.json")
    
    if should_build:
        print(f"Build needed for missing instruction sets: {', '.join(missing_sets)}")
        sys.exit(0)
    else:
        print("No build needed - all instruction set versions exist")
        sys.exit(1)

if __name__ == "__main__":
    main() 