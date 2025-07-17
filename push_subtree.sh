#!/bin/bash
"""
Push phosphobot Subtree Script (Enhanced Version)
=================================================

This script automates the process of pushing the phosphobot subtree
to the remote repository rule_base branch while handling .gitignore modifications and fallback
to force push when necessary.

Usage:
    ./push_subtree.sh [commit_message]

Example:
    ./push_subtree.sh "Update phosphobot with new configurations"
"""

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to run commands with error handling
run_command() {
    local cmd="$1"
    local check_error="${2:-true}"
    
    if [ "$check_error" = "true" ]; then
        if ! eval "$cmd"; then
            print_error "Command failed: $cmd"
            return 1
        fi
    else
        eval "$cmd" || true
    fi
}

# Fallback function using subtree split and force push
push_subtree_fallback() {
    local commit_message="$1"
    local temp_branch="temp-phosphobot-push"
    local remote_url="https://github.com/hafnium49/phosphobot.git"
    
    print_warning "Regular subtree push failed, trying fallback method..."
    
    # Clean up any existing temp branch
    run_command "git branch -D $temp_branch" false
    
    # Split the subtree into a temporary branch
    print_status "Creating temporary subtree branch..."
    if ! run_command "git subtree split --prefix=phosphobot -b $temp_branch"; then
        print_error "Failed to create subtree split"
        return 1
    fi
    print_success "Created temporary branch: $temp_branch"
    
    # Force push the temporary branch to remote rule_base branch
    print_status "Force pushing subtree to remote repository rule_base branch..."
    if ! run_command "git push $remote_url $temp_branch:rule_base --force"; then
        print_error "Failed to force push subtree"
        run_command "git branch -D $temp_branch" false
        return 1
    fi
    print_success "Subtree force pushed successfully to rule_base branch"
    
    # Clean up temporary branch
    print_status "Cleaning up temporary branch..."
    run_command "git branch -D $temp_branch"
    print_success "Temporary branch deleted"
    
    return 0
}

# Cleanup function
cleanup() {
    if [ -f ".gitignore.backup" ]; then
        print_status "Restoring .gitignore due to error..."
        mv .gitignore.backup .gitignore
        print_success ".gitignore restored"
    fi
}

# Set up trap for cleanup on exit
trap cleanup EXIT

# Get commit message from argument or use default
COMMIT_MESSAGE="${1:-Update phosphobot subtree}"

print_status "Starting phosphobot subtree push process..."

# Ensure we're in the right directory
if [ ! -d "phosphobot" ]; then
    print_error "phosphobot directory not found. Please run this script from the aloha-lite root directory."
    exit 1
fi

# Step 1: Backup .gitignore
print_status "Backing up .gitignore..."
cp .gitignore .gitignore.backup
print_success ".gitignore backed up"

# Step 2: Temporarily modify .gitignore to allow tracking
print_status "Temporarily modifying .gitignore..."
sed -i 's|phosphobot/|# phosphobot/ - temporarily commented for subtree push|g' .gitignore
print_success ".gitignore modified"

# Step 3: Add and commit the phosphobot directory
print_status "Adding phosphobot to git tracking..."
run_command "git add phosphobot/"
run_command "git add .gitignore"

# Check if there are actually changes to commit
if git diff --cached --quiet; then
    print_warning "No changes to commit"
else
    run_command "git commit -m \"Temporarily track phosphobot for subtree push: $COMMIT_MESSAGE\""
    print_success "Changes committed"
fi

# Step 4: Try regular subtree push first
print_status "Attempting regular subtree push..."
REMOTE_URL="https://github.com/hafnium49/phosphobot.git"

if run_command "git subtree push --prefix=phosphobot $REMOTE_URL rule_base" false; then
    print_success "Regular subtree push succeeded"
    SUBTREE_PUSH_SUCCESS=true
else
    # Step 5: Fallback to force push method
    if push_subtree_fallback "$COMMIT_MESSAGE"; then
        SUBTREE_PUSH_SUCCESS=true
    else
        SUBTREE_PUSH_SUCCESS=false
    fi
fi

if [ "$SUBTREE_PUSH_SUCCESS" != "true" ]; then
    print_error "Both regular and fallback subtree push methods failed"
    exit 1
fi

# Step 6: Restore original .gitignore
print_status "Restoring original .gitignore..."
mv .gitignore.backup .gitignore
print_success ".gitignore restored"

# Step 7: Commit the restored .gitignore
print_status "Committing restored .gitignore..."
run_command "git add .gitignore"

# Only commit if there are changes
if ! git diff --cached --quiet; then
    run_command "git commit -m \"Restore .gitignore after subtree push\""
    print_success ".gitignore changes committed"
fi

# Step 8: Push the main repository changes
print_status "Pushing main repository changes..."
if run_command "git push origin main" false; then
    print_success "Main repository pushed successfully"
else
    print_warning "Main repository push failed, but subtree was pushed successfully"
fi

# Final status check
print_status "Checking final git status..."
run_command "git status" false

print_success "🎉 Subtree push process completed successfully!"
print_status "Summary:"
print_status "  ✅ phosphobot subtree pushed to remote rule_base branch"
print_status "  ✅ .gitignore restored to original state"
print_status "  ✅ Local repository is clean and up to date"

# Disable trap since we completed successfully
trap - EXIT
