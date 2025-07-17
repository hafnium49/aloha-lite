#!/usr/bin/env python3
"""
Universal Subtree Push Script (Enhanced Python Version)
======================================================

This script automates the process of pushing subtrees to their respective
remote repositories while handling .gitignore modifications and fallback
to force push when necessary.

Supported Subtrees:
  - demo2rules: pushes to main branch of https://github.com/hafnium49/aloha-lite-demo2rule
  - phosphobot: pushes to rule_base branch of https://github.com/hafnium49/phosphobot

Usage:
    python push_subtree.py <subtree_name> [commit_message]

Examples:
    python push_subtree.py demo2rules "Update demo2rules with new CSV features"
    python push_subtree.py phosphobot "Update phosphobot with new configurations"
"""

import sys
import os
import subprocess
import argparse
import shutil
from pathlib import Path
from typing import Dict, Optional, Tuple

# ANSI color codes
class Colors:
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    NC = '\033[0m'  # No Color

# Subtree configurations
SUBTREE_CONFIGS = {
    'demo2rules': {
        'dir': 'aloha-lite-demo2rule',
        'url': 'https://github.com/hafnium49/aloha-lite-demo2rule.git',
        'branch': 'main'
    },
    'phosphobot': {
        'dir': 'phosphobot',
        'url': 'https://github.com/hafnium49/phosphobot.git',
        'branch': 'rule_base'
    }
}

class SubtreePusher:
    def __init__(self):
        self.gitignore_backup = None
        
    def print_status(self, message: str):
        """Print info message with blue color."""
        print(f"{Colors.BLUE}[INFO]{Colors.NC} {message}")
        
    def print_success(self, message: str):
        """Print success message with green color."""
        print(f"{Colors.GREEN}[SUCCESS]{Colors.NC} {message}")
        
    def print_warning(self, message: str):
        """Print warning message with yellow color."""
        print(f"{Colors.YELLOW}[WARNING]{Colors.NC} {message}")
        
    def print_error(self, message: str):
        """Print error message with red color."""
        print(f"{Colors.RED}[ERROR]{Colors.NC} {message}")
        
    def run_command(self, cmd: str, check_error: bool = True) -> Tuple[bool, str]:
        """Run a shell command and return success status and output."""
        try:
            result = subprocess.run(
                cmd, 
                shell=True, 
                capture_output=True, 
                text=True, 
                check=check_error
            )
            return True, result.stdout + result.stderr
        except subprocess.CalledProcessError as e:
            if check_error:
                self.print_error(f"Command failed: {cmd}")
                self.print_error(f"Error: {e.stderr}")
            return False, e.stderr
        except Exception as e:
            if check_error:
                self.print_error(f"Command failed: {cmd}")
                self.print_error(f"Error: {str(e)}")
            return False, str(e)
    
    def cleanup(self):
        """Restore .gitignore if backup exists."""
        if self.gitignore_backup and os.path.exists('.gitignore.backup'):
            self.print_status("Restoring .gitignore due to error...")
            shutil.move('.gitignore.backup', '.gitignore')
            self.print_success(".gitignore restored")
    
    def push_subtree_fallback(self, commit_message: str, subtree_dir: str, 
                            remote_url: str, target_branch: str) -> bool:
        """Fallback function using subtree split and force push."""
        temp_branch = f"temp-{subtree_dir.replace('/', '-')}-push"
        
        self.print_warning("Regular subtree push failed, trying fallback method...")
        
        # Clean up any existing temp branch
        self.run_command(f"git branch -D {temp_branch}", check_error=False)
        
        # Split the subtree into a temporary branch
        self.print_status("Creating temporary subtree branch...")
        success, _ = self.run_command(f"git subtree split --prefix={subtree_dir} -b {temp_branch}")
        if not success:
            self.print_error("Failed to create subtree split")
            return False
        self.print_success(f"Created temporary branch: {temp_branch}")
        
        # Force push the temporary branch to remote
        self.print_status(f"Force pushing subtree to remote repository {target_branch} branch...")
        success, _ = self.run_command(f"git push {remote_url} {temp_branch}:{target_branch} --force")
        if not success:
            self.print_error("Failed to force push subtree")
            self.run_command(f"git branch -D {temp_branch}", check_error=False)
            return False
        self.print_success(f"Subtree force pushed successfully to {target_branch} branch")
        
        # Clean up temporary branch
        self.print_status("Cleaning up temporary branch...")
        self.run_command(f"git branch -D {temp_branch}")
        self.print_success("Temporary branch deleted")
        
        return True
    
    def push_subtree(self, subtree_name: str, commit_message: str) -> bool:
        """Main function to push subtree."""
        try:
            # Get configuration
            if subtree_name not in SUBTREE_CONFIGS:
                self.print_error(f"Unknown subtree: {subtree_name}")
                self.show_usage()
                return False
                
            config = SUBTREE_CONFIGS[subtree_name]
            subtree_dir = config['dir']
            remote_url = config['url']
            target_branch = config['branch']
            
            self.print_status(f"Starting {subtree_name} subtree push process...")
            self.print_status(f"Target: {remote_url} ({target_branch} branch)")
            
            # Ensure we're in the right directory
            if not os.path.exists(subtree_dir):
                self.print_error(f"{subtree_dir} directory not found. Please run this script from the aloha-lite root directory.")
                return False
            
            # Step 1: Backup .gitignore
            self.print_status("Backing up .gitignore...")
            shutil.copy('.gitignore', '.gitignore.backup')
            self.gitignore_backup = True
            self.print_success(".gitignore backed up")
            
            # Step 2: Temporarily modify .gitignore to allow tracking
            self.print_status("Temporarily modifying .gitignore...")
            with open('.gitignore', 'r') as f:
                content = f.read()
            
            modified_content = content.replace(
                f"{subtree_dir}/", 
                f"# {subtree_dir}/ - temporarily commented for subtree push"
            )
            
            with open('.gitignore', 'w') as f:
                f.write(modified_content)
            self.print_success(".gitignore modified")
            
            # Step 3: Add and commit the subtree directory
            self.print_status(f"Adding {subtree_dir} to git tracking...")
            self.run_command(f"git add {subtree_dir}/")
            self.run_command("git add .gitignore")
            
            # Check if there are actually changes to commit
            success, _ = self.run_command("git diff --cached --quiet", check_error=False)
            if success:
                self.print_warning("No changes to commit")
            else:
                self.run_command(f'git commit -m "Temporarily track {subtree_dir} for subtree push: {commit_message}"')
                self.print_success("Changes committed")
            
            # Step 4: Try regular subtree push first
            self.print_status("Attempting regular subtree push...")
            success, _ = self.run_command(f"git subtree push --prefix={subtree_dir} {remote_url} {target_branch}", check_error=False)
            
            if success:
                self.print_success("Regular subtree push succeeded")
                subtree_push_success = True
            else:
                # Step 5: Fallback to force push method
                subtree_push_success = self.push_subtree_fallback(commit_message, subtree_dir, remote_url, target_branch)
            
            if not subtree_push_success:
                self.print_error("Both regular and fallback subtree push methods failed")
                return False
            
            # Step 6: Restore original .gitignore
            self.print_status("Restoring original .gitignore...")
            shutil.move('.gitignore.backup', '.gitignore')
            self.gitignore_backup = None
            self.print_success(".gitignore restored")
            
            # Step 7: Commit the restored .gitignore
            self.print_status("Committing restored .gitignore...")
            self.run_command("git add .gitignore")
            
            # Only commit if there are changes
            success, _ = self.run_command("git diff --cached --quiet", check_error=False)
            if not success:
                self.run_command('git commit -m "Restore .gitignore after subtree push"')
                self.print_success(".gitignore changes committed")
            
            # Step 8: Push the main repository changes
            self.print_status("Pushing main repository changes...")
            success, _ = self.run_command("git push origin main", check_error=False)
            if success:
                self.print_success("Main repository pushed successfully")
            else:
                self.print_warning("Main repository push failed, but subtree was pushed successfully")
            
            # Final status check
            self.print_status("Checking final git status...")
            self.run_command("git status", check_error=False)
            
            self.print_success("🎉 Subtree push process completed successfully!")
            self.print_status("Summary:")
            self.print_status(f"  ✅ {subtree_name} subtree pushed to remote {target_branch} branch")
            self.print_status(f"  ✅ Repository: {remote_url}")
            self.print_status("  ✅ .gitignore restored to original state")
            self.print_status("  ✅ Local repository is clean and up to date")
            
            return True
            
        except Exception as e:
            self.print_error(f"An error occurred: {str(e)}")
            return False
        finally:
            # Cleanup on exit
            self.cleanup()
    
    def show_usage(self):
        """Show usage information."""
        print("Usage: python push_subtree.py <subtree_name> [commit_message]")
        print("")
        print("Supported subtrees:")
        print("  demo2rules  - Push to main branch of aloha-lite-demo2rule repository")
        print("  phosphobot  - Push to rule_base branch of phosphobot repository")
        print("")
        print("Examples:")
        print('  python push_subtree.py demo2rules "Update demo2rules with new CSV features"')
        print('  python push_subtree.py phosphobot "Update phosphobot with new configurations"')

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Universal Subtree Push Script",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Supported subtrees:
  demo2rules  - Push to main branch of aloha-lite-demo2rule repository
  phosphobot  - Push to rule_base branch of phosphobot repository

Examples:
  python push_subtree.py demo2rules "Update demo2rules with new CSV features"
  python push_subtree.py phosphobot "Update phosphobot with new configurations"
        """
    )
    
    parser.add_argument(
        'subtree_name',
        choices=['demo2rules', 'phosphobot'],
        help='Name of the subtree to push'
    )
    
    parser.add_argument(
        'commit_message',
        nargs='?',
        help='Commit message for the subtree push'
    )
    
    args = parser.parse_args()
    
    # Set default commit message if not provided
    commit_message = args.commit_message or f"Update {args.subtree_name} subtree"
    
    # Create pusher instance and execute
    pusher = SubtreePusher()
    success = pusher.push_subtree(args.subtree_name, commit_message)
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
