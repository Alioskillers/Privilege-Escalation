#!/bin/bash

# ============================================================================
# 🔐 Access Control Security Simulator - Complete Setup Script
# ============================================================================
# This script sets up the entire project environment including:
# - Python version check
# - Virtual environment creation
# - Dependencies installation
# - Project verification
# ============================================================================

set -e  # Exit on any error

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Functions
print_header() {
    echo -e "\n${BLUE}═══════════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}\n"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Check Python version
check_python() {
    print_header "Step 1: Checking Python Installation"
    
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 is not installed!"
        echo "Please install Python 3.8 or higher from https://www.python.org"
        exit 1
    fi
    
    PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
    print_info "Found Python $PYTHON_VERSION"
    
    # Check if version is 3.8 or higher
    if ! python3 -c 'import sys; exit(0 if sys.version_info >= (3, 8) else 1)' 2>/dev/null; then
        print_error "Python 3.8 or higher is required (found Python $PYTHON_VERSION)"
        exit 1
    fi
    
    print_success "Python version check passed"
}

# Create virtual environment
create_venv() {
    print_header "Step 2: Setting Up Virtual Environment"
    
    if [ -d ".venv" ]; then
        print_warning "Virtual environment already exists at .venv"
        read -p "Do you want to recreate it? (y/n) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            print_info "Removing existing virtual environment..."
            rm -rf .venv
        else
            print_info "Using existing virtual environment"
            return 0
        fi
    fi
    
    print_info "Creating virtual environment..."
    python3 -m venv .venv
    print_success "Virtual environment created"
}

# Activate virtual environment
activate_venv() {
    print_info "Activating virtual environment..."
    source .venv/bin/activate
    print_success "Virtual environment activated"
}

# Upgrade pip
upgrade_pip() {
    print_header "Step 3: Upgrading pip"
    
    print_info "Upgrading pip, setuptools, and wheel..."
    .venv/bin/python -m pip install --upgrade pip setuptools wheel --quiet
    print_success "pip upgraded successfully"
}

# Install requirements
install_requirements() {
    print_header "Step 4: Installing Project Dependencies"
    
    if [ ! -f "requirements.txt" ]; then
        print_error "requirements.txt not found!"
        exit 1
    fi
    
    print_info "Installing packages from requirements.txt..."
    .venv/bin/pip install -r requirements.txt --quiet
    print_success "All dependencies installed successfully"
}

# Verify installation
verify_installation() {
    print_header "Step 5: Verifying Installation"
    
    print_info "Checking installed packages..."
    .venv/bin/pip list | grep -E "(streamlit|numpy|networkx|matplotlib)" || {
        print_error "Some packages are missing!"
        exit 1
    }
    
    print_success "All required packages are installed"
}

# Verify project structure
verify_structure() {
    print_header "Step 6: Verifying Project Structure"
    
    local missing=0
    
    # Check required files
    local required_files=("app.py" "requirements.txt" "backend/rbac.py" "backend/matrix_model.py" "backend/privilege_analysis.py" "data/sample_permissions.json")
    
    for file in "${required_files[@]}"; do
        if [ -f "$file" ]; then
            print_success "Found $file"
        else
            print_warning "Missing $file"
            ((missing++))
        fi
    done
    
    if [ $missing -gt 0 ]; then
        print_warning "Some files are missing, but setup can continue"
    else
        print_success "All expected files are present"
    fi
}

# Final summary
print_summary() {
    print_header "Setup Complete! 🎉"
    
    echo -e "${GREEN}Your project is ready to run!${NC}\n"
    
    echo "To start the application, run one of the following commands:\n"
    echo -e "${BLUE}Option 1: Using the run script${NC}"
    echo -e "  ${YELLOW}./run.sh${NC}\n"
    
    echo -e "${BLUE}Option 2: Manual start${NC}"
    echo -e "  ${YELLOW}source .venv/bin/activate${NC}"
    echo -e "  ${YELLOW}streamlit run app.py${NC}\n"
    
    echo "The app will be available at: http://localhost:8501"
    echo ""
}

# ============================================================================
# Main execution
# ============================================================================

main() {
    clear
    echo -e "${BLUE}"
    cat << "EOF"
    ╔═══════════════════════════════════════════════════════════╗
    ║     🔐 Access Control Security Simulator Setup 🔐        ║
    ║         Complete Project Configuration Script            ║
    ╚═══════════════════════════════════════════════════════════╝
EOF
    echo -e "${NC}\n"
    
    print_info "Starting complete project setup...\n"
    
    # Get the directory where the script is located
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    cd "$SCRIPT_DIR"
    
    # Run all setup steps
    check_python
    create_venv
    activate_venv
    upgrade_pip
    install_requirements
    verify_installation
    verify_structure
    print_summary
}

# Run main function
main "$@"
