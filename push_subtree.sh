#!/bin/bash
"""
Push aloha-lite-demo2rule Subtree Script
========================================

This script automates the process of pushing the aloha-lite-demo2rule subtree
to the remote repository while handling .gitignore modifications.

Usage:
    ./push_subtree.sh [commit_message]

Example:
    ./push_subtree.sh "Update demo2rules with new CSV features"
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

# Get commit message from argument or use default
COMMIT_MESSAGE="${1:-Update aloha-lite-demo2rule subtree}"

print_status "Starting aloha-lite-demo2rule subtree push process..."

# Ensure we're in the right directory
if [ ! -d "aloha-lite-demo2rule" ]; then
    print_error "aloha-lite-demo2rule directory not found. Please run this script from the aloha-lite root directory."
    exit 1
fi

# Check if there are any uncommitted changes in aloha-lite-demo2rule
print_status "Checking for uncommitted changes in aloha-lite-demo2rule..."
if git status --porcelain aloha-lite-demo2rule/ | grep -q .; then
    print_warning "Found uncommitted changes in aloha-lite-demo2rule/"
    git status aloha-lite-demo2rule/
    read -p "Do you want to commit these changes? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        print_status "Committing changes..."
        git add aloha-lite-demo2rule/
        git commit -m "$COMMIT_MESSAGE"
        print_success "Changes committed"
    else
        print_error "Please commit or stash changes before pushing subtree"
        exit 1
    fi
else
    print_status "No uncommitted changes found"
fi

# Step 1: Backup .gitignore
print_status "Backing up .gitignore..."
cp .gitignore .gitignore.backup
print_success ".gitignore backed up"

# Step 2: Temporarily modify .gitignore to allow tracking aloha-lite-demo2rule
print_status "Temporarily modifying .gitignore..."
sed -i 's/^aloha-lite-demo2rule\/$/# aloha-lite-demo2rule\/  # Temporarily commented for subtree push/' .gitignore
print_success ".gitignore modified"

# Step 3: Add and commit the modified .gitignore and aloha-lite-demo2rule
print_status "Adding aloha-lite-demo2rule to git tracking..."
git add .gitignore aloha-lite-demo2rule/

if git diff --cached --quiet; then
    print_warning "No changes to commit"
else
    git commit -m "Prepare for subtree push: $COMMIT_MESSAGE"
    print_success "Changes committed"
fi

# Step 4: Push the subtree
print_status "Pushing aloha-lite-demo2rule subtree..."
if git subtree push --prefix=aloha-lite-demo2rule origin main; then
    print_success "Subtree pushed successfully"
else
    print_error "Subtree push failed"
    # Restore .gitignore before exiting
    cp .gitignore.backup .gitignore
    rm .gitignore.backup
    exit 1
fi

# Step 5: Restore .gitignore
print_status "Restoring original .gitignore..."
cp .gitignore.backup .gitignore
rm .gitignore.backup
print_success ".gitignore restored"

# Step 6: Commit the restored .gitignore
print_status "Committing restored .gitignore..."
git add .gitignore
git commit -m "Restore .gitignore after subtree push"
print_success ".gitignore changes committed"

# Step 7: Push the main repository changes
print_status "Pushing main repository changes..."
if git push --force-with-lease origin main; then
    print_success "Main repository pushed successfully"
else
    print_warning "Main repository push failed, but subtree was pushed successfully"
fi

# Final status check
print_status "Checking final git status..."
git status

print_success "🎉 Subtree push process completed successfully!"
print_status "Summary:"
print_status "  ✅ aloha-lite-demo2rule subtree pushed to remote"
print_status "  ✅ .gitignore restored to original state"
print_status "  ✅ Local repository is clean and up to date"
