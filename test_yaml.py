#!/usr/bin/env python3
"""
Simple YAML syntax validator for GitHub Actions workflows
"""

import sys

def test_yaml_syntax():
    """Test YAML syntax of workflow files"""
    try:
        # Try to import yaml module
        import yaml
    except ImportError:
        print("PyYAML not installed, skipping syntax validation")
        return True
    
    workflow_files = [
        '.github/workflows/build.yml',
        '.github/workflows/benchmark.yml'
    ]
    
    for file_path in workflow_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                yaml.safe_load(f)
            print(f"✅ {file_path} - YAML syntax is valid")
        except Exception as e:
            print(f"❌ {file_path} - YAML syntax error: {e}")
            return False
    
    return True

if __name__ == "__main__":
    success = test_yaml_syntax()
    sys.exit(0 if success else 1) 