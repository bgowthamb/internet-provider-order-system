#!/bin/bash

# GitHub Setup Script for Internet Provider Order Entry System
# This script will help you set up your project on GitHub

echo "🚀 Setting up GitHub repository for Internet Provider Order Entry System"
echo "=================================================================="

# Check if git is available
if ! command -v git &> /dev/null; then
    echo "❌ Git is not installed. Please install Xcode command line tools first:"
    echo "   xcode-select --install"
    exit 1
fi

echo "✅ Git is available"

# Check if we're in the right directory
if [ ! -f "run.py" ] || [ ! -f "README.md" ]; then
    echo "❌ Please run this script from the internet-provider-order-system directory"
    exit 1
fi

echo "✅ In correct directory"

# Initialize git repository
echo "📁 Initializing git repository..."
git init

# Add all files
echo "📝 Adding files to git..."
git add .

# Check status
echo "📊 Git status:"
git status

# Make initial commit
echo "💾 Making initial commit..."
git commit -m "Initial commit: Internet Provider Order Entry System

- Complete Flask application with ML-powered pricing optimization
- Customer churn prediction and competitor analysis
- Order management with dynamic pricing
- Role-based access control and RESTful API
- Comprehensive documentation and sample data"

echo ""
echo "🎉 Local git repository is ready!"
echo ""
echo "📋 Next steps:"
echo "1. Go to GitHub.com and create a new repository"
echo "2. Run these commands (replace YOUR_USERNAME with your GitHub username):"
echo ""
echo "   git remote add origin https://github.com/YOUR_USERNAME/internet-provider-order-system.git"
echo "   git branch -M main"
echo "   git push -u origin main"
echo ""
echo "📖 For detailed instructions, see: GITHUB_SETUP.md"
echo ""
echo "🔗 Quick GitHub repository creation:"
echo "   https://github.com/new"
echo ""
