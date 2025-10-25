#!/usr/bin/env python3
"""
Test runner script for the MoneyMoney library.

This script provides convenient ways to run different types of tests
and manage the test environment.
"""

import argparse
import os
import subprocess
import sys
from pathlib import Path


def run_command(cmd, description):
    """Run a command and handle errors."""
    print(f"\n{'='*60}")
    print(f"Running: {description}")
    print(f"Command: {' '.join(cmd)}")
    print(f"{'='*60}")
    
    result = subprocess.run(cmd, capture_output=False)
    if result.returncode != 0:
        print(f"\n❌ {description} failed with exit code {result.returncode}")
        return False
    else:
        print(f"\n✅ {description} completed successfully")
        return True


def check_moneymoney_installed():
    """Check if MoneyMoney application is installed."""
    return os.path.exists("/Applications/MoneyMoney.app")


def main():
    parser = argparse.ArgumentParser(description="Run MoneyMoney library tests")
    parser.add_argument(
        "--type",
        choices=["unit", "integration", "all", "coverage"],
        default="unit",
        help="Type of tests to run"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Run tests in verbose mode"
    )
    parser.add_argument(
        "--coverage",
        action="store_true",
        help="Generate coverage report"
    )
    parser.add_argument(
        "--lint",
        action="store_true",
        help="Run linting checks"
    )
    parser.add_argument(
        "--clean",
        action="store_true",
        help="Clean up test artifacts"
    )
    
    args = parser.parse_args()
    
    # Change to project root
    project_root = Path(__file__).parent.parent
    os.chdir(project_root)
    
    # Base pytest command
    base_cmd = ["pipenv", "run", "pytest"]
    
    if args.verbose:
        base_cmd.append("-v")
    
    if args.coverage or args.type == "coverage":
        base_cmd.extend(["--cov=money", "--cov-report=term-missing", "--cov-report=html"])
    
    success = True
    
    # Run linting if requested
    if args.lint:
        lint_commands = [
            (["pipenv", "run", "flake8", "money/", "tests/"], "Flake8 linting"),
            (["pipenv", "run", "pylint", "money/", "tests/"], "Pylint linting"),
            (["pipenv", "run", "ruff", "check", "money/", "tests/"], "Ruff linting"),
        ]
        
        for cmd, desc in lint_commands:
            if not run_command(cmd, desc):
                success = False
    
    # Run tests based on type
    if args.type == "unit":
        cmd = base_cmd + ["tests/", "-m", "not integration"]
        success &= run_command(cmd, "Unit tests")
        
    elif args.type == "integration":
        if not check_moneymoney_installed():
            print("\n⚠️  MoneyMoney application not found. Integration tests will be skipped.")
            print("   To run integration tests, install MoneyMoney from the App Store.")
        else:
            cmd = base_cmd + ["tests/", "-m", "integration"]
            success &= run_command(cmd, "Integration tests")
            
    elif args.type == "all":
        cmd = base_cmd + ["tests/"]
        success &= run_command(cmd, "All tests")
        
    elif args.type == "coverage":
        cmd = base_cmd + ["tests/", "--cov=money", "--cov-report=term-missing", "--cov-report=html", "--cov-report=xml"]
        success &= run_command(cmd, "Tests with coverage")
    
    # Clean up if requested
    if args.clean:
        cleanup_commands = [
            (["rm", "-rf", "htmlcov/"], "Remove HTML coverage report"),
            (["rm", "-f", "coverage.xml"], "Remove XML coverage report"),
            (["rm", "-rf", ".pytest_cache/"], "Remove pytest cache"),
            (["rm", "-rf", "__pycache__/"], "Remove Python cache"),
            (["find", ".", "-name", "*.pyc", "-delete"], "Remove .pyc files"),
        ]
        
        for cmd, desc in cleanup_commands:
            run_command(cmd, desc)
    
    # Summary
    print(f"\n{'='*60}")
    if success:
        print("🎉 All requested operations completed successfully!")
    else:
        print("❌ Some operations failed. Check the output above for details.")
        sys.exit(1)
    print(f"{'='*60}")


if __name__ == "__main__":
    main()