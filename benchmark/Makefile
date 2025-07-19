# Benchmark Makefile

.PHONY: help run run-local clean build-images build-all-images results

# Default target
help:
	@echo "Available targets:"
	@echo "  run              - Run full benchmark with Docker Compose"
	@echo "  run-local        - Run benchmark locally (requires local images)"
	@echo "  build-images     - Build all benchmark images"
	@echo "  build-all-images - Build all Thorium instruction set images"
	@echo "  clean            - Clean up benchmark containers and results"
	@echo "  results          - Show latest benchmark results"

# Run full benchmark with Docker Compose
run:
	@echo "Starting benchmark with Docker Compose..."
	@mkdir -p results
	docker-compose -f docker-compose.benchmark.yml up --build
	@echo "Benchmark completed. Check results/ directory for output."

# Run benchmark locally (requires local images)
run-local:
	@echo "Running benchmark locally..."
	@mkdir -p results
	python3 benchmark.py \
		--iterations 3 \
		--output results/benchmark_results.json \
		--report results/benchmark_report.md \
		--urls https://www.google.com https://www.github.com https://www.stackoverflow.com

# Build all benchmark images
build-images:
	@echo "Building benchmark images..."
	docker-compose -f docker-compose.benchmark.yml build

# Build all Thorium instruction set images
build-all-images:
	@echo "Building all Thorium instruction set images..."
	cd .. && make build-all

# Clean up benchmark containers and results
clean:
	@echo "Cleaning up benchmark containers..."
	docker-compose -f docker-compose.benchmark.yml down -v
	docker rm -f benchmark-chromedp benchmark-thorium-avx2 benchmark-thorium-avx benchmark-thorium-sse3 benchmark-thorium-sse4 benchmark-runner 2>/dev/null || true
	@echo "Cleaning up results..."
	rm -rf results/*.json results/*.md 2>/dev/null || true

# Show latest benchmark results
results:
	@echo "Latest benchmark results:"
	@if [ -f "results/benchmark_report.md" ]; then \
		cat results/benchmark_report.md; \
	else \
		echo "No benchmark results found. Run 'make run' first."; \
	fi

# Quick benchmark (single iteration)
quick:
	@echo "Running quick benchmark..."
	@mkdir -p results
	python3 benchmark.py \
		--iterations 1 \
		--output results/quick_benchmark.json \
		--report results/quick_report.md \
		--urls https://www.google.com

# Performance comparison
compare:
	@echo "Running performance comparison..."
	@mkdir -p results
	python3 benchmark.py \
		--iterations 5 \
		--output results/comparison_results.json \
		--report results/comparison_report.md \
		--urls https://www.google.com https://www.github.com https://www.stackoverflow.com https://www.wikipedia.org

# Install dependencies
install:
	@echo "Installing Python dependencies..."
	pip install -r requirements.txt

# Setup benchmark environment
setup: install
	@echo "Setting up benchmark environment..."
	@mkdir -p results
	@echo "Benchmark environment ready!"

# Run specific container benchmark
benchmark-chromedp:
	@echo "Benchmarking chromedp/headless-shell..."
	python3 benchmark.py \
		--iterations 3 \
		--output results/chromedp_benchmark.json \
		--report results/chromedp_report.md \
		--urls https://www.google.com https://www.github.com

benchmark-thorium-avx2:
	@echo "Benchmarking Thorium AVX2..."
	python3 benchmark.py \
		--iterations 3 \
		--output results/thorium_avx2_benchmark.json \
		--report results/thorium_avx2_report.md \
		--urls https://www.google.com https://www.github.com

# Generate summary report
summary:
	@echo "Generating summary report..."
	@if [ -f "results/benchmark_results.json" ]; then \
		python3 -c "import json; data=json.load(open('results/benchmark_results.json')); \
		print('=== BENCHMARK SUMMARY ==='); \
		for result in data['results']: \
			if result['success']: \
				startup = result['startup']['total_startup_time']; \
				load_times = [r['load_time'] for r in result['page_loads'] if r['success']]; \
				avg_load = sum(load_times)/len(load_times) if load_times else 0; \
				print(f'{result[\"image\"]}: Startup={startup:.2f}s, Avg Load={avg_load:.2f}s'); \
			else: \
				print(f'{result[\"image\"]}: FAILED'); \
		"; \
	else \
		echo "No benchmark results found. Run 'make run' first."; \
	fi 