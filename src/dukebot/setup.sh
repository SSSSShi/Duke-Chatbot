#!/bin/bash

# DukeBot Security Framework Setup Script
# This script helps you set up the secure DukeBot environment

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_NAME="dukebot-secure"
PYTHON_VERSION="3.11"
VENV_NAME="venv"

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

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to generate encryption key
generate_encryption_key() {
    python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
}

# Function to create directory structure
create_directories() {
    print_status "Creating directory structure..."
    
    mkdir -p logs
    mkdir -p data
    mkdir -p tests
    mkdir -p docs
    mkdir -p resources
    mkdir -p config
    
    print_success "Directory structure created"
}

# Function to check Python version
check_python() {
    print_status "Checking Python installation..."
    
    if ! command_exists python3; then
        print_error "Python 3 is not installed. Please install Python 3.11 or later."
        exit 1
    fi
    
    PYTHON_VER=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
    print_success "Python $PYTHON_VER found"
    
    if [[ "$PYTHON_VER" < "3.11" ]]; then
        print_warning "Python 3.11+ is recommended. Current version: $PYTHON_VER"
    fi
}

# Function to create virtual environment
create_venv() {
    print_status "Creating virtual environment..."
    
    if [ -d "$VENV_NAME" ]; then
        print_warning "Virtual environment already exists. Skipping creation."
        return
    fi
    
    python3 -m venv $VENV_NAME
    print_success "Virtual environment created in $VENV_NAME/"
}

# Function to activate virtual environment
activate_venv() {
    print_status "Activating virtual environment..."
    
    if [ -f "$VENV_NAME/bin/activate" ]; then
        source $VENV_NAME/bin/activate
        print_success "Virtual environment activated"
    else
        print_error "Virtual environment not found. Please run: python3 -m venv $VENV_NAME"
        exit 1
    fi
}

# Function to install dependencies
install_dependencies() {
    print_status "Installing Python dependencies..."
    
    if [ ! -f "requirements.txt" ]; then
        print_error "requirements.txt not found. Please ensure it exists in the current directory."
        exit 1
    fi
    
    pip install --upgrade pip
    pip install -r requirements.txt
    
    print_success "Dependencies installed successfully"
}

# Function to setup environment file
setup_environment() {
    print_status "Setting up environment configuration..."
    
    if [ -f ".env" ]; then
        print_warning ".env file already exists. Backing up to .env.backup"
        cp .env .env.backup
    fi
    
    # Copy example environment file
    if [ -f ".env.example" ]; then
        cp .env.example .env
    else
        # Create basic .env file
        cat > .env << EOF
# DukeBot Configuration
STAGE=development
DEBUG=true
LOG_LEVEL=DEBUG

# Security Settings
ENCRYPTION_KEY=$(generate_encryption_key)
RATE_LIMIT_REQUESTS=20
SESSION_TIMEOUT=3600

# API Keys (REPLACE WITH ACTUAL VALUES)
SERPAPI_API_KEY=your_serpapi_key_here

# Privacy Settings
DATA_RETENTION_DAYS=7
PRIVACY_MODE=strict
AUDIT_LOG_ENABLED=true

# Development Settings
HTTPS_ONLY=false
CORS_ORIGINS=http://localhost:8501,http://127.0.0.1:8501
EOF
    fi
    
    print_success "Environment file created: .env"
    print_warning "Please edit .env and add your actual API keys!"
}

# Function to setup resource files
setup_resources() {
    print_status "Setting up resource files..."
    
    # Create example resource files if they don't exist
    if [ ! -f "resources/subjects.txt" ]; then
        echo "Creating example subjects.txt..."
        cat > resources/subjects.txt << EOF
AIPI - Artificial Intelligence for Product Innovation
COMPSCI - Computer Science
ECE - Electrical and Computer Engineering
MENG - Master of Engineering
MATH - Mathematics
STAT - Statistics
EOF
    fi
    
    if [ ! -f "resources/groups.txt" ]; then
        echo "Creating example groups.txt..."
        cat > resources/groups.txt << EOF
+DataScience (+DS)
+ArtificialIntelligence (+AI)
+Engineering
+ComputerScience
All
EOF
    fi
    
    if [ ! -f "resources/categories.txt" ]; then
        echo "Creating example categories.txt..."
        cat > resources/categories.txt << EOF
Academic Calendar Dates
Alumni/Reunion
Artificial Intelligence
Computer Science
Data Science
Engineering
Lectures
Seminars
All
EOF
    fi
    
    print_success "Resource files created"
}

# Function to run tests
run_tests() {
    print_status "Running tests..."
    
    if command_exists pytest; then
        pytest tests/ -v --cov=. --cov-report=html
        print_success "Tests completed. Coverage report generated in htmlcov/"
    else
        print_warning "pytest not found. Install it with: pip install pytest pytest-cov"
    fi
}

# Function to setup Docker
setup_docker() {
    if command_exists docker; then
        print_status "Setting up Docker..."
        
        # Build Docker image
        docker build -t dukebot:secure-latest .
        
        print_success "Docker image built: dukebot:secure-latest"
        
        print_status "You can run the container with:"
        echo "docker run -p 8501:8501 --env-file .env dukebot:secure-latest"
    else
        print_warning "Docker not found. Skipping Docker setup."
    fi
}

# Function to validate setup
validate_setup() {
    print_status "Validating setup..."
    
    # Check if required files exist
    required_files=(
        "security_privacy.py"
        "secure_agent.py" 
        "secure_ui.py"
        "tools.py"
        ".env"
    )
    
    for file in "${required_files[@]}"; do
        if [ ! -f "$file" ]; then
            print_error "Required file missing: $file"
            exit 1
        fi
    done
    
    # Check if .env has been configured
    if grep -q "your_serpapi_key_here" .env; then
        print_warning "Please update SERPAPI_API_KEY in .env with your actual API key"
    fi
    
    print_success "Setup validation completed"
}

# Function to show usage instructions
show_usage() {
    echo ""
    print_success "Setup completed successfully!"
    echo ""
    echo "Next steps:"
    echo "1. Edit .env file and add your actual API keys:"
    echo "   - SERPAPI_API_KEY"
    echo ""
    echo "2. To run the application locally:"
    echo "   source $VENV_NAME/bin/activate"
    echo "   streamlit run secure_ui.py"
    echo ""
    echo "3. To run tests:"
    echo "   pytest tests/ -v"
    echo ""
    echo "4. For Docker deployment:"
    echo "   docker run -p 8501:8501 --env-file .env dukebot:secure-latest"
    echo ""
    echo "5. For AWS Lambda deployment:"
    echo "   serverless deploy"
    echo ""
    echo "6. For Kubernetes deployment:"
    echo "   kubectl apply -f k8s-deployment.yaml"
    echo ""
}

# Main function
main() {
    echo "=========================================="
    echo "    DukeBot Security Framework Setup     "
    echo "=========================================="
    echo ""
    
    # Parse command line arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            --skip-tests)
                SKIP_TESTS=true
                shift
                ;;
            --skip-docker)
                SKIP_DOCKER=true
                shift
                ;;
            --production)
                ENVIRONMENT=production
                shift
                ;;
            -h|--help)
                echo "Usage: $0 [options]"
                echo "Options:"
                echo "  --skip-tests    Skip running tests"
                echo "  --skip-docker   Skip Docker setup"
                echo "  --production    Setup for production environment"
                echo "  -h, --help      Show this help message"
                exit 0
                ;;
            *)
                print_error "Unknown option: $1"
                exit 1
                ;;
        esac
    done
    
    # Run setup steps
    check_python
    create_directories
    create_venv
    activate_venv
    install_dependencies
    setup_environment
    setup_resources
    validate_setup
    
    # Optional steps
    if [ "$SKIP_TESTS" != true ]; then
        run_tests
    fi
    
    if [ "$SKIP_DOCKER" != true ]; then
        setup_docker
    fi
    
    show_usage
}

# Handle script interruption
trap 'print_error "Setup interrupted"; exit 1' INT TERM

# Run main function
main "$@"