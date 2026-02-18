#!/bin/bash

# ═══════════════════════════════════════════════════════════════════
# Imtiaz Mart - Build & Test Script
# ═══════════════════════════════════════════════════════════════════

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SERVICES=("product-service" "user-service" "order-service" "inventory-service" "payment-service")
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
INFRASTRUCTURE_DIR="${PROJECT_ROOT}/infrastructure"

# Default version (can be overridden)
VERSION="${VERSION:-1.0.0}"
BUILD_DATE=$(date -u +"%Y-%m-%d")

# ═══════════════════════════════════════════════════════════════════
# Helper Functions
# ═══════════════════════════════════════════════════════════════════

print_header() {
    echo -e "${BLUE}"
    echo "═══════════════════════════════════════════════════════════════════"
    echo "  $1"
    echo "═══════════════════════════════════════════════════════════════════"
    echo -e "${NC}"
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

# ═══════════════════════════════════════════════════════════════════
# Version Management
# ═══════════════════════════════════════════════════════════════════

increment_version() {
    local version=$1
    local type=$2  # major, minor, patch
    
    IFS='.' read -r -a parts <<< "$version"
    local major="${parts[0]}"
    local minor="${parts[1]}"
    local patch="${parts[2]}"
    
    case $type in
        major)
            major=$((major + 1))
            minor=0
            patch=0
            ;;
        minor)
            minor=$((minor + 1))
            patch=0
            ;;
        patch)
            patch=$((patch + 1))
            ;;
    esac
    
    echo "${major}.${minor}.${patch}"
}

# ═══════════════════════════════════════════════════════════════════
# Cleanup Functions
# ═══════════════════════════════════════════════════════════════════

cleanup_venv() {
    print_header "Cleaning Local .venv Folders"
    
    for service in "${SERVICES[@]}"; do
        local venv_path="${PROJECT_ROOT}/services/${service}/.venv"
        if [ -d "$venv_path" ]; then
            print_info "Removing ${service}/.venv..."
            sudo rm -rf "$venv_path"
        fi
    done
    
    print_success "All .venv folders cleaned!"
}

cleanup_docker() {
    print_header "Cleaning Docker Resources"
    
    cd "$INFRASTRUCTURE_DIR"
    
    print_info "Stopping containers..."
    docker compose down --remove-orphans
    
    print_info "Removing dangling images..."
    docker image prune -f
    
    print_success "Docker cleanup complete!"
}

# ═══════════════════════════════════════════════════════════════════
# Build Functions
# ═══════════════════════════════════════════════════════════════════

build_service() {
    local service=$1
    local version=$2
    
    print_info "Building ${service} v${version}..."
    
    cd "$INFRASTRUCTURE_DIR"
    
    # Build with version
    BUILD_DATE="$BUILD_DATE" VERSION="$version" \
        docker compose build --no-cache "$service"
    
    if [ $? -eq 0 ]; then
        print_success "${service} v${version} built successfully!"
        return 0
    else
        print_error "Failed to build ${service}"
        return 1
    fi
}

build_all() {
    print_header "Building All Services (v${VERSION})"
    
    cleanup_venv
    cleanup_docker
    
    local failed_services=()
    
    for service in "${SERVICES[@]}"; do
        if ! build_service "$service" "$VERSION"; then
            failed_services+=("$service")
        fi
    done
    
    if [ ${#failed_services[@]} -eq 0 ]; then
        print_success "All services built successfully!"
        return 0
    else
        print_error "Failed services: ${failed_services[*]}"
        return 1
    fi
}

# ═══════════════════════════════════════════════════════════════════
# Start/Stop Functions
# ═══════════════════════════════════════════════════════════════════

start_services() {
    print_header "Starting All Services"
    
    cd "$INFRASTRUCTURE_DIR"
    docker compose up -d
    
    print_info "Waiting for services to be healthy..."
    sleep 15
    
    print_success "Services started!"
    docker compose ps
}

stop_services() {
    print_header "Stopping All Services"
    
    cd "$INFRASTRUCTURE_DIR"
    docker compose down
    
    print_success "Services stopped!"
}

# ═══════════════════════════════════════════════════════════════════
# Local Development Setup
# ═══════════════════════════════════════════════════════════════════

setup_local_venv() {
    print_header "Setting Up Local Development Environment"
    
    for service in "${SERVICES[@]}"; do
        print_info "Setting up ${service}..."
        
        cd "${PROJECT_ROOT}/services/${service}"
        
        # Create venv
        uv venv
        
        # Install dependencies
        uv sync
        
        print_success "${service} local environment ready!"
    done
}

# ═══════════════════════════════════════════════════════════════════
# Testing Functions
# ═══════════════════════════════════════════════════════════════════

test_service() {
    local service=$1
    
    print_info "Testing ${service}..."
    
    cd "${PROJECT_ROOT}/services/${service}"
    
    # Run tests
    if uv run pytest tests/ -v --tb=short; then
        print_success "${service} tests passed!"
        return 0
    else
        print_error "${service} tests failed!"
        return 1
    fi
}

test_all() {
    print_header "Running Tests for All Services"
    
    local failed_tests=()
    
    for service in "${SERVICES[@]}"; do
        if ! test_service "$service"; then
            failed_tests+=("$service")
        fi
    done
    
    if [ ${#failed_tests[@]} -eq 0 ]; then
        print_success "All tests passed! 🎉"
        return 0
    else
        print_error "Failed tests: ${failed_tests[*]}"
        return 1
    fi
}

# ═══════════════════════════════════════════════════════════════════
# Health Check Functions
# ═══════════════════════════════════════════════════════════════════

check_health() {
    print_header "Checking Service Health"
    
    local services_health=(
        "product-service:8001"
        "user-service:8000"
        "payment-service:8002"
        "order-service:8003"
        "inventory-service:8004"
    )
    
    for item in "${services_health[@]}"; do
        IFS=':' read -r service port <<< "$item"
        
        if curl -s "http://localhost:${port}/health" > /dev/null 2>&1 || \
           curl -s "http://localhost:${port}/" > /dev/null 2>&1; then
            print_success "${service} is healthy (port ${port})"
        else
            print_error "${service} is not responding (port ${port})"
        fi
    done
}

# ═══════════════════════════════════════════════════════════════════
# Main Workflows
# ═══════════════════════════════════════════════════════════════════

full_build_and_test() {
    print_header "Full Build & Test Workflow (v${VERSION})"
    
    # Build
    if ! build_all; then
        print_error "Build failed! Exiting..."
        exit 1
    fi
    
    # Start services
    start_services
    
    # Setup local environment
    setup_local_venv
    
    # Check health
    check_health
    
    # Run tests
    if ! test_all; then
        print_error "Tests failed!"
        exit 1
    fi
    
    print_success "Full build & test completed successfully! 🎉"
}

quick_test() {
    print_header "Quick Test (No Rebuild)"
    
    # Just run tests with existing setup
    test_all
}

# ═══════════════════════════════════════════════════════════════════
# Usage
# ═══════════════════════════════════════════════════════════════════

show_usage() {
    cat << USAGE
Imtiaz Mart - Build & Test Script

Usage: ./build-and-test.sh [command] [options]

Commands:
    build               Build all services with current version
    build <service>     Build specific service
    test                Run tests for all services
    test <service>      Run tests for specific service
    start               Start all services
    stop                Stop all services
    restart             Restart all services
    health              Check health of all services
    clean               Clean Docker resources and .venv folders
    setup               Setup local development environment
    full                Full build, start, setup, and test workflow
    quick               Quick test without rebuild
    
Version Management:
    --version <ver>     Set version (default: 1.0.0)
    --patch             Increment patch version (1.0.0 -> 1.0.1)
    --minor             Increment minor version (1.0.0 -> 1.1.0)
    --major             Increment major version (1.0.0 -> 2.0.0)

Examples:
    # Build all services with version 1.0.0
    ./build-and-test.sh build
    
    # Build with specific version
    VERSION=1.2.0 ./build-and-test.sh build
    
    # Increment patch and build
    ./build-and-test.sh build --patch
    
    # Full workflow with new minor version
    ./build-and-test.sh full --minor
    
    # Build specific service
    ./build-and-test.sh build product-service
    
    # Test specific service
    ./build-and-test.sh test user-service
    
    # Quick test (no rebuild)
    ./build-and-test.sh quick
USAGE
}

# ═══════════════════════════════════════════════════════════════════
# Main Script Logic
# ═══════════════════════════════════════════════════════════════════

main() {
    # Check for version flags
    for arg in "$@"; do
        case $arg in
            --patch)
                VERSION=$(increment_version "$VERSION" "patch")
                print_info "Version bumped to: $VERSION"
                ;;
            --minor)
                VERSION=$(increment_version "$VERSION" "minor")
                print_info "Version bumped to: $VERSION"
                ;;
            --major)
                VERSION=$(increment_version "$VERSION" "major")
                print_info "Version bumped to: $VERSION"
                ;;
            --version)
                shift
                VERSION=$1
                print_info "Version set to: $VERSION"
                ;;
        esac
    done
    
    # Parse command
    local command=${1:-help}
    local target=${2:-}
    
    case $command in
        build)
            if [ -n "$target" ] && [[ " ${SERVICES[@]} " =~ " ${target} " ]]; then
                build_service "$target" "$VERSION"
            else
                build_all
            fi
            ;;
        test)
            if [ -n "$target" ] && [[ " ${SERVICES[@]} " =~ " ${target} " ]]; then
                test_service "$target"
            else
                test_all
            fi
            ;;
        start)
            start_services
            ;;
        stop)
            stop_services
            ;;
        restart)
            stop_services
            start_services
            ;;
        health)
            check_health
            ;;
        clean)
            cleanup_docker
            cleanup_venv
            ;;
        setup)
            setup_local_venv
            ;;
        full)
            full_build_and_test
            ;;
        quick)
            quick_test
            ;;
        help|--help|-h)
            show_usage
            ;;
        *)
            print_error "Unknown command: $command"
            show_usage
            exit 1
            ;;
    esac
}

# Run main
main "$@"
