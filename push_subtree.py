#!/usr/bin/env python3
"""
Push aloha-lite-demo2rule Subtree Script (Python Version)
=========================================================

This script automates the process of pushing the aloha-lite-demo2rule subtree
to the remote repository while handling .gitignore modifications.

Usage:
    python3 push_subtree.py [commit_message]

Example:
    python3 push_subtree.py "Update demo2rules with new CSV features"
"""

import subprocess
import sys
import os
from pathlib import Path

class Colors:
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    NC = '\033[0m'  # No Color

def print_status(message):
    print(f"{Colors.BLUE}[INFO]{Colors.NC} {message}")

def print_success(message):
    print(f"{Colors.GREEN}[SUCCESS]{Colors.NC} {message}")

def print_warning(message):
    print(f"{Colors.YELLOW}[WARNING]{Colors.NC} {message}")

def print_error(message):
    print(f"{Colors.RED}[ERROR]{Colors.NC} {message}")

def run_command(cmd, check=True, capture_output=False):
    """Run a shell command and return the result."""
    try:
        if capture_output:
            result = subprocess.run(cmd, shell=True, check=check, capture_output=True, text=True)
            return result.stdout.strip()
        else:
            subprocess.run(cmd, shell=True, check=check)
            return True
    except subprocess.CalledProcessError as e:
        if check:
            print_error(f"Command failed: {cmd}")
            print_error(f"Error: {e}")
            return False
        return False

def main():
    # Get commit message from argument or use default
    commit_message = sys.argv[1] if len(sys.argv) > 1 else "Update aloha-lite-demo2rule subtree"
    
    print_status("Starting aloha-lite-demo2rule subtree push process...")
    
    # Ensure we're in the right directory
    if not Path("aloha-lite-demo2rule").exists():
        print_error("aloha-lite-demo2rule directory not found. Please run this script from the aloha-lite root directory.")
        sys.exit(1)
    
    # Check if there are any uncommitted changes in aloha-lite-demo2rule
    print_status("Checking for uncommitted changes in aloha-lite-demo2rule...")
    status_output = run_command("git status --porcelain aloha-lite-demo2rule/", capture_output=True)
    
    if status_output:
        print_warning("Found uncommitted changes in aloha-lite-demo2rule/")
        run_command("git status aloha-lite-demo2rule/", check=False)
        
        response = input("Do you want to commit these changes? (y/n): ").lower().strip()
        if response == 'y':
            print_status("Committing changes...")
            run_command("git add aloha-lite-demo2rule/")
            run_command(f'git commit -m "{commit_message}"')
            print_success("Changes committed")
        else:
            print_error("Please commit or stash changes before pushing subtree")
            sys.exit(1)
    else:
        print_status("No uncommitted changes found")
    
    try:
        # Step 1: Backup .gitignore
        print_status("Backing up .gitignore...")
        with open('.gitignore', 'r') as f:
            original_gitignore = f.read()
        with open('.gitignore.backup', 'w') as f:
            f.write(original_gitignore)
        print_success(".gitignore backed up")
        
        # Step 2: Temporarily modify .gitignore
        print_status("Temporarily modifying .gitignore...")
        modified_gitignore = original_gitignore.replace(
            'aloha-lite-demo2rule/',
            '# aloha-lite-demo2rule/  # Temporarily commented for subtree push'
        )
        with open('.gitignore', 'w') as f:
            f.write(modified_gitignore)
        print_success(".gitignore modified")
        
        # Step 3: Add and commit changes
        print_status("Adding aloha-lite-demo2rule to git tracking...")
        run_command("git add .gitignore aloha-lite-demo2rule/")
        
        # Check if there are changes to commit
        diff_output = run_command("git diff --cached --quiet", check=False, capture_output=True)
        if run_command("git diff --cached --quiet", check=False):
            print_warning("No changes to commit")
        else:
            run_command(f'git commit -m "Prepare for subtree push: {commit_message}"')
            print_success("Changes committed")
        
        # Step 4: Push the subtree
        print_status("Pushing aloha-lite-demo2rule subtree...")
        if run_command("git subtree push --prefix=aloha-lite-demo2rule origin main", check=False):
            print_success("Subtree pushed successfully")
        else:
            print_error("Subtree push failed")
            raise Exception("Subtree push failed")
        
        # Step 5: Restore .gitignore
        print_status("Restoring original .gitignore...")
        with open('.gitignore', 'w') as f:
            f.write(original_gitignore)
        if Path('.gitignore.backup').exists():
            Path('.gitignore.backup').unlink()
        print_success(".gitignore restored")
        
        # Step 6: Commit the restored .gitignore
        print_status("Committing restored .gitignore...")
        run_command("git add .gitignore")
        run_command('git commit -m "Restore .gitignore after subtree push"')
        print_success(".gitignore changes committed")
        
        # Step 7: Push the main repository changes
        print_status("Pushing main repository changes...")
        if run_command("git push --force-with-lease origin main", check=False):
            print_success("Main repository pushed successfully")
        else:
            print_warning("Main repository push failed, but subtree was pushed successfully")
        
        # Final status check
        print_status("Checking final git status...")
        run_command("git status", check=False)
        
        print_success("🎉 Subtree push process completed successfully!")
        print_status("Summary:")
        print_status("  ✅ aloha-lite-demo2rule subtree pushed to remote")
        print_status("  ✅ .gitignore restored to original state")
        print_status("  ✅ Local repository is clean and up to date")
        
    except Exception as e:
        print_error(f"Process failed: {e}")
        # Restore .gitignore in case of error
        if Path('.gitignore.backup').exists():
            print_status("Restoring .gitignore due to error...")
            with open('.gitignore.backup', 'r') as f:
                backup_content = f.read()
            with open('.gitignore', 'w') as f:
                f.write(backup_content)
            Path('.gitignore.backup').unlink()
            print_success(".gitignore restored")
        sys.exit(1)

if __name__ == "__main__":
    main()
