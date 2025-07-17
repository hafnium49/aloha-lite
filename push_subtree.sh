#!/bin/bash
"""
Universal Subtree Push Script (Enhanced Version)
===============================================

This script automates the process of pushing subtrees to their respective
remote repositories while handling .gitignore modifications and fallback
to force push when necessary.

Supported Subtrees:
  - demo2rules: pushes to main branch of https://github.com/hafnium49/aloha-lite-demo2rule
  - phosphobot: pushes to rule_base branch of https://github.com/hafnium49/phosphobot

Usage:
    ./push_subtree.sh <subtree_name> [commit_message]

Examples:
    ./push_subtree.sh demo2rules "Update demo2rules with new CSV features"
    ./push_subtree.sh phosphobot "Update phosphobot with new configurations"
"""

set -e  # Exit on any error

# Subtree configurations
declare -A SUBTREE_CONFIGS
SUBTREE_CONFIGS[demo2rules_dir]="aloha-lite-demo2rule"
SUBTREE_CONFIGS[demo2rules_url]="https://github.com/hafnium49/aloha-lite-demo2rule.git"
SUBTREE_CONFIGS[demo2rules_branch]="main"

SUBTREE_CONFIGS[phosphobot_dir]="phosphobot"
SUBTREE_CONFIGS[phosphobot_url]="https://github.com/hafnium49/phosphobot.git"
SUBTREE_CONFIGS[phosphobot_branch]="rule_base"

# Function to show usage
show_usage() {
    echo "Usage: $0 <subtree_name> [commit_message]"
    echo ""
    echo "Supported subtrees:"
    echo "  demo2rules  - Push to main branch of aloha-lite-demo2rule repository"
    echo "  phosphobot  - Push to rule_base branch of phosphobot repository"
    echo ""
    echo "Examples:"
    echo "  $0 demo2rules \"Update demo2rules with new CSV features\""
    echo "  $0 phosphobot \"Update phosphobot with new configurations\""
    exit 1
}

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
    local subtree_dir="$2"
    local remote_url="$3"
    local target_branch="$4"
    local temp_branch="temp-${subtree_dir//\//-}-push"
    
    print_warning "Regular subtree push failed, trying fallback method..."
    
    # Clean up any existing temp branch
    run_command "git branch -D $temp_branch" false
    
    # Split the subtree into a temporary branch
    print_status "Creating temporary subtree branch..."
    if ! run_command "git subtree split --prefix=$subtree_dir -b $temp_branch"; then
        print_error "Failed to create subtree split"
        return 1
    fi
    print_success "Created temporary branch: $temp_branch"
    
    # Force push the temporary branch to remote
    print_status "Force pushing subtree to remote repository $target_branch branch..."
    if ! run_command "git push $remote_url $temp_branch:$target_branch --force"; then
        print_error "Failed to force push subtree"
        run_command "git branch -D $temp_branch" false
        return 1
    fi
    print_success "Subtree force pushed successfully to $target_branch branch"
    
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

# Parse command line arguments
if [ $# -lt 1 ]; then
    print_error "Missing required argument: subtree_name"
    show_usage
fi

SUBTREE_NAME="$1"
COMMIT_MESSAGE="${2:-Update $SUBTREE_NAME subtree}"

# Validate subtree name and get configuration
case "$SUBTREE_NAME" in
    "demo2rules")
        SUBTREE_DIR="${SUBTREE_CONFIGS[demo2rules_dir]}"
        REMOTE_URL="${SUBTREE_CONFIGS[demo2rules_url]}"
        TARGET_BRANCH="${SUBTREE_CONFIGS[demo2rules_branch]}"
        ;;
    "phosphobot")
        SUBTREE_DIR="${SUBTREE_CONFIGS[phosphobot_dir]}"
        REMOTE_URL="${SUBTREE_CONFIGS[phosphobot_url]}"
        TARGET_BRANCH="${SUBTREE_CONFIGS[phosphobot_branch]}"
        ;;
    *)
        print_error "Unknown subtree: $SUBTREE_NAME"
        show_usage
        ;;
esac

print_status "Starting $SUBTREE_NAME subtree push process..."
print_status "Target: $REMOTE_URL ($TARGET_BRANCH branch)"

# Ensure we're in the right directory
if [ ! -d "$SUBTREE_DIR" ]; then
    print_error "$SUBTREE_DIR directory not found. Please run this script from the aloha-lite root directory."
    exit 1
fi

# Step 1: Backup .gitignore
print_status "Backing up .gitignore..."
cp .gitignore .gitignore.backup
print_success ".gitignore backed up"

# Step 2: Temporarily modify .gitignore to allow tracking
print_status "Temporarily modifying .gitignore..."
sed -i "s|${SUBTREE_DIR}/|# ${SUBTREE_DIR}/ - temporarily commented for subtree push|g" .gitignore
print_success ".gitignore modified"

# Step 3: Add and commit the subtree directory
print_status "Adding $SUBTREE_DIR to git tracking..."
run_command "git add $SUBTREE_DIR/"
run_command "git add .gitignore"

# Check if there are actually changes to commit
if git diff --cached --quiet; then
    print_warning "No changes to commit"
else
    run_command "git commit -m \"Temporarily track $SUBTREE_DIR for subtree push: $COMMIT_MESSAGE\""
    print_success "Changes committed"
fi

# Step 4: Try regular subtree push first
print_status "Attempting regular subtree push..."

if run_command "git subtree push --prefix=$SUBTREE_DIR $REMOTE_URL $TARGET_BRANCH" false; then
    print_success "Regular subtree push succeeded"
    SUBTREE_PUSH_SUCCESS=true
else
    # Step 5: Fallback to force push method
    if push_subtree_fallback "$COMMIT_MESSAGE" "$SUBTREE_DIR" "$REMOTE_URL" "$TARGET_BRANCH"; then
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
print_status "  ✅ $SUBTREE_NAME subtree pushed to remote $TARGET_BRANCH branch"
print_status "  ✅ Repository: $REMOTE_URL"
print_status "  ✅ .gitignore restored to original state"
print_status "  ✅ Local repository is clean and up to date"

# Disable trap since we completed successfully
trap - EXIT
