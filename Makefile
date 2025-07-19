# Thorium Docker Makefile

.PHONY: help build build-all build-avx2 build-avx build-sse3 build-sse4 test clean push version-check run run-avx2 run-avx run-sse3 run-sse4 stop benchmark benchmark-quick benchmark-compare

# Default target
help:
	@echo "Available targets:"
	@echo "  build         - Build Docker image (default: AVX2)"
	@echo "  build-all     - Build all instruction set versions"
	@echo "  build-avx2    - Build AVX2 version"
	@echo "  build-avx     - Build AVX version"
	@echo "  build-sse3    - Build SSE3 version"
	@echo "  build-sse4    - Build SSE4 version"
	@echo "  test          - Run tests"
	@echo "  clean         - Clean up containers and images"
	@echo "  push          - Push to Docker Hub"
	@echo "  version-check - Check for latest Thorium version"
	@echo "  run           - Run AVX2 container locally"
	@echo "  run-avx2      - Run AVX2 container"
	@echo "  run-avx       - Run AVX container"
	@echo "  run-sse3      - Run SSE3 container"
	@echo "  run-sse4      - Run SSE4 container"
	@echo "  stop          - Stop running containers"
	@echo "  benchmark     - Run performance benchmark"
	@echo "  benchmark-quick - Run quick benchmark"
	@echo "  benchmark-compare - Run detailed comparison"

# Build Docker image (default: AVX2)
build:
	@echo "Building Thorium Docker image (AVX2)..."
	docker build -t thorium-docker:latest .

# Build all instruction set versions
build-all: build-avx2 build-avx build-sse3 build-sse4
	@echo "All instruction set versions built successfully!"

# Build AVX2 version
build-avx2:
	@echo "Building Thorium Docker image (AVX2)..."
	docker build --build-arg INSTRUCTION_SET=AVX2 -t thorium-docker:avx2 .

# Build AVX version
build-avx:
	@echo "Building Thorium Docker image (AVX)..."
	docker build --build-arg INSTRUCTION_SET=AVX -t thorium-docker:avx .

# Build SSE3 version
build-sse3:
	@echo "Building Thorium Docker image (SSE3)..."
	docker build --build-arg INSTRUCTION_SET=SSE3 -t thorium-docker:sse3 .

# Build SSE4 version
build-sse4:
	@echo "Building Thorium Docker image (SSE4)..."
	docker build --build-arg INSTRUCTION_SET=SSE4 -t thorium-docker:sse4 .

# Build with specific version
build-version:
	@echo "Building Thorium Docker image with version $(VERSION)..."
	docker build --build-arg THORIUM_VERSION=$(VERSION) --build-arg INSTRUCTION_SET=$(INSTRUCTION_SET) -t thorium-docker:$(VERSION)-$(INSTRUCTION_SET) .

# Run tests
test:
	@echo "Running tests..."
	docker-compose up -d thorium-test
	@echo "Waiting for browser to start..."
	@sleep 15
	python3 test/test_browser.py
	docker-compose down

# Clean up
clean:
	@echo "Cleaning up..."
	docker-compose down -v
	docker system prune -f
	docker image prune -f

# Push to Docker Hub
push:
	@echo "Pushing to Docker Hub..."
	docker tag thorium-docker:latest $(DOCKER_USERNAME)/thorium-docker:latest
	docker tag thorium-docker:avx2 $(DOCKER_USERNAME)/thorium-docker:avx2
	docker tag thorium-docker:avx $(DOCKER_USERNAME)/thorium-docker:avx
	docker tag thorium-docker:sse3 $(DOCKER_USERNAME)/thorium-docker:sse3
	docker tag thorium-docker:sse4 $(DOCKER_USERNAME)/thorium-docker:sse4
	docker push $(DOCKER_USERNAME)/thorium-docker:latest
	docker push $(DOCKER_USERNAME)/thorium-docker:avx2
	docker push $(DOCKER_USERNAME)/thorium-docker:avx
	docker push $(DOCKER_USERNAME)/thorium-docker:sse3
	docker push $(DOCKER_USERNAME)/thorium-docker:sse4

# Check latest version
version-check:
	@echo "Checking latest Thorium version..."
	python3 scripts/check_version.py

# Run AVX2 container locally (default)
run: run-avx2

# Run AVX2 container
run-avx2:
	@echo "Starting Thorium AVX2 container..."
	docker-compose up -d thorium-headless-avx2
	@echo "Container started. Remote debugging available at http://localhost:9222"

# Run AVX container
run-avx:
	@echo "Starting Thorium AVX container..."
	docker-compose up -d thorium-headless-avx
	@echo "Container started. Remote debugging available at http://localhost:9223"

# Run SSE3 container
run-sse3:
	@echo "Starting Thorium SSE3 container..."
	docker-compose up -d thorium-headless-sse3
	@echo "Container started. Remote debugging available at http://localhost:9224"

# Run SSE4 container
run-sse4:
	@echo "Starting Thorium SSE4 container..."
	docker-compose up -d thorium-headless-sse4
	@echo "Container started. Remote debugging available at http://localhost:9225"

# Stop containers
stop:
	@echo "Stopping containers..."
	docker-compose down

# Install dependencies
install:
	@echo "Installing Python dependencies..."
	pip install -r requirements.txt

# Development setup
dev-setup: install
	@echo "Setting up development environment..."
	mkdir -p test
	@echo "Development environment ready!"

# Build and test
all: build test

# Show instruction set info
info:
	@echo "Available instruction sets:"
	@echo "  AVX2  - High Performance (recommended for modern CPUs)"
	@echo "  AVX   - Medium Performance (good compatibility)"
	@echo "  SSE3  - Basic Performance (wider compatibility)"
	@echo "  SSE4  - Compatibility (maximum compatibility)"
	@echo ""
	@echo "Usage examples:"
	@echo "  make build-avx2    # Build AVX2 version"
	@echo "  make run-avx2      # Run AVX2 container"
	@echo "  make build-all     # Build all versions"

# Performance benchmark
benchmark:
	@echo "Running performance benchmark..."
	@if [ ! -d "benchmark" ]; then \
		echo "Benchmark directory not found. Please ensure benchmark tools are available."; \
		exit 1; \
	fi
	cd benchmark && make run

# Quick benchmark
benchmark-quick:
	@echo "Running quick performance benchmark..."
	@if [ ! -d "benchmark" ]; then \
		echo "Benchmark directory not found. Please ensure benchmark tools are available."; \
		exit 1; \
	fi
	cd benchmark && make quick

# Detailed comparison benchmark
benchmark-compare:
	@echo "Running detailed performance comparison..."
	@if [ ! -d "benchmark" ]; then \
		echo "Benchmark directory not found. Please ensure benchmark tools are available."; \
		exit 1; \
	fi
	cd benchmark && make compare

# Show benchmark results
benchmark-results:
	@echo "Showing benchmark results..."
	@if [ ! -d "benchmark" ]; then \
		echo "Benchmark directory not found. Please ensure benchmark tools are available."; \
		exit 1; \
	fi
	cd benchmark && make results

# Generate benchmark summary
benchmark-summary:
	@echo "Generating benchmark summary..."
	@if [ ! -d "benchmark" ]; then \
		echo "Benchmark directory not found. Please ensure benchmark tools are available."; \
		exit 1; \
	fi
	cd benchmark && make summary

# Clean benchmark
benchmark-clean:
	@echo "Cleaning benchmark environment..."
	@if [ ! -d "benchmark" ]; then \
		echo "Benchmark directory not found. Please ensure benchmark tools are available."; \
		exit 1; \
	fi
	cd benchmark && make clean

# Setup benchmark environment
benchmark-setup:
	@echo "Setting up benchmark environment..."
	@if [ ! -d "benchmark" ]; then \
		echo "Benchmark directory not found. Please ensure benchmark tools are available."; \
		exit 1; \
	fi
	cd benchmark && make setup 