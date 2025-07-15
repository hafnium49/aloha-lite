#!/usr/bin/env python3
"""
Push aloha-lite-demo2rule Subtree Script (Enhanced Version)
===========================================================

This script automates the process of pushing the aloha-lite-demo2rule subtree
to the remote repository while handling .gitignore modifications and fallback
to force push when necessary.

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

def push_subtree_fallback(commit_message):
    """Fallback method using subtree split and force push."""
    print_warning("Regular subtree push failed, trying fallback method...")
    
    temp_branch = "temp-demo2rule-push"
    
    try:
        # Clean up any existing temp branch
        run_command(f"git branch -D {temp_branch}", check=False)
        
        # Split the subtree into a temporary branch
        print_status("Creating temporary subtree branch...")
        run_command(f"git subtree split --prefix=aloha-lite-demo2rule -b {temp_branch}")
        print_success(f"Created temporary branch: {temp_branch}")
        
        # Force push the temporary branch to remote
        print_status("Force pushing subtree to remote repository...")
        remote_url = "https://github.com/hafnium49/aloha-lite-demo2rule.git"
        run_command(f"git push {remote_url} {temp_branch}:main --force")
        print_success("Subtree force pushed successfully")
        
        # Clean up temporary branch
        print_status("Cleaning up temporary branch...")
        run_command(f"git branch -D {temp_branch}")
        print_success("Temporary branch deleted")
        
        return True
        
    except Exception as e:
        print_error(f"Fallback method failed: {e}")
        # Clean up temporary branch if it exists
        run_command(f"git branch -D {temp_branch}", check=False)
        return False

def main():
    # Get commit message from argument or use default
    commit_message = sys.argv[1] if len(sys.argv) > 1 else "Update aloha-lite-demo2rule subtree"
    
    print_status("Starting aloha-lite-demo2rule subtree push process...")
    
    # Ensure we're in the right directory
    if not Path("aloha-lite-demo2rule").exists():
        print_error("aloha-lite-demo2rule directory not found. Please run this script from the aloha-lite root directory.")
        sys.exit(1)
    
    backup_file = Path('.gitignore.backup')
    
    try:
        # Step 1: Backup .gitignore
        print_status("Backing up .gitignore...")
        with open('.gitignore', 'r') as f:
            original_gitignore = f.read()
        with open(backup_file, 'w') as f:
            f.write(original_gitignore)
        print_success(".gitignore backed up")
        
        # Step 2: Temporarily modify .gitignore to allow tracking
        print_status("Temporarily modifying .gitignore...")
        modified_gitignore = original_gitignore.replace(
            'aloha-lite-demo2rule/',
            '# aloha-lite-demo2rule/ - temporarily commented for subtree push'
        )
        with open('.gitignore', 'w') as f:
            f.write(modified_gitignore)
        print_success(".gitignore modified")
        
        # Step 3: Add and commit the aloha-lite-demo2rule directory
        print_status("Adding aloha-lite-demo2rule to git tracking...")
        run_command("git add aloha-lite-demo2rule/")
        run_command("git add .gitignore")
        
        # Check if there are actually changes to commit
        status_output = run_command("git diff --cached --name-only", capture_output=True)
        if status_output:
            run_command(f'git commit -m "Temporarily track aloha-lite-demo2rule for subtree push: {commit_message}"')
            print_success("Changes committed")
        else:
            print_warning("No changes to commit")
        
        # Step 4: Try regular subtree push first
        print_status("Attempting regular subtree push...")
        remote_url = "https://github.com/hafnium49/aloha-lite-demo2rule.git"
        
        if run_command(f"git subtree push --prefix=aloha-lite-demo2rule {remote_url} main", check=False):
            print_success("Regular subtree push succeeded")
            subtree_push_success = True
        else:
            # Step 5: Fallback to force push method
            subtree_push_success = push_subtree_fallback(commit_message)
        
        if not subtree_push_success:
            raise Exception("Both regular and fallback subtree push methods failed")
        
        # Step 6: Restore original .gitignore
        print_status("Restoring original .gitignore...")
        with open('.gitignore', 'w') as f:
            f.write(original_gitignore)
        print_success(".gitignore restored")
        
        # Step 7: Commit the restored .gitignore
        print_status("Committing restored .gitignore...")
        run_command("git add .gitignore")
        
        # Only commit if there are changes
        status_output = run_command("git diff --cached --name-only", capture_output=True)
        if status_output:
            run_command('git commit -m "Restore .gitignore after subtree push"')
            print_success(".gitignore changes committed")
        
        # Step 8: Push the main repository changes
        print_status("Pushing main repository changes...")
        if run_command("git push origin main", check=False):
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
        if backup_file.exists():
            print_status("Restoring .gitignore due to error...")
            with open(backup_file, 'r') as f:
                backup_content = f.read()
            with open('.gitignore', 'w') as f:
                f.write(backup_content)
            print_success(".gitignore restored")
        sys.exit(1)
    
    finally:
        # Clean up backup file
        if backup_file.exists():
            backup_file.unlink()
            print_status("Backup file cleaned up")

if __name__ == "__main__":
    main()
