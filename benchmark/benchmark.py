#!/usr/bin/env python3
"""
Performance benchmark script for comparing Thorium Docker containers
with chromedp/docker-headless-shell and different instruction sets.
"""

import json
import time
import subprocess
import requests
import psutil
import statistics
from datetime import datetime
from typing import Dict, List, Any
import argparse
import sys
import os

class BenchmarkRunner:
    """Performance benchmark runner for headless browser containers."""
    
    def __init__(self, iterations: int = 5, timeout: int = 30):
        self.iterations = iterations
        self.timeout = timeout
        self.results = {}
        
    def run_command(self, cmd: List[str], timeout: int = None) -> Dict[str, Any]:
        """Run a command and return execution details."""
        start_time = time.time()
        start_memory = psutil.virtual_memory().used
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout or self.timeout
            )
            
            end_time = time.time()
            end_memory = psutil.virtual_memory().used
            
            return {
                'success': result.returncode == 0,
                'stdout': result.stdout,
                'stderr': result.stderr,
                'returncode': result.returncode,
                'execution_time': end_time - start_time,
                'memory_delta': end_memory - start_memory,
                'start_time': start_time,
                'end_time': end_time
            }
        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'stdout': '',
                'stderr': 'Command timed out',
                'returncode': -1,
                'execution_time': timeout or self.timeout,
                'memory_delta': 0,
                'start_time': start_time,
                'end_time': time.time()
            }
        except Exception as e:
            return {
                'success': False,
                'stdout': '',
                'stderr': str(e),
                'returncode': -1,
                'execution_time': 0,
                'memory_delta': 0,
                'start_time': start_time,
                'end_time': time.time()
            }
    
    def start_container(self, image: str, name: str, port: int) -> Dict[str, Any]:
        """Start a container and measure startup time."""
        print(f"Starting container: {image}")
        
        # Stop and remove existing container
        self.run_command(['docker', 'stop', name], timeout=10)
        self.run_command(['docker', 'rm', name], timeout=10)
        
        # Start container
        cmd = [
            'docker', 'run', '-d',
            '--name', name,
            '-p', f'{port}:9222',
            '--security-opt', 'seccomp=unconfined',
            '--cap-add', 'SYS_ADMIN',
            '--shm-size', '2G',
            image
        ]
        
        result = self.run_command(cmd)
        
        if result['success']:
            # Wait for container to be ready
            ready_time = self.wait_for_container_ready(port)
            result['ready_time'] = ready_time
            result['total_startup_time'] = result['execution_time'] + ready_time
        else:
            result['ready_time'] = 0
            result['total_startup_time'] = result['execution_time']
        
        return result
    
    def wait_for_container_ready(self, port: int, max_wait: int = 60) -> float:
        """Wait for container to be ready and return wait time."""
        start_time = time.time()
        url = f'http://localhost:{port}/json/version'
        
        while time.time() - start_time < max_wait:
            try:
                response = requests.get(url, timeout=5)
                if response.status_code == 200:
                    return time.time() - start_time
            except:
                pass
            time.sleep(1)
        
        return max_wait
    
    def test_page_load(self, port: int, url: str) -> Dict[str, Any]:
        """Test page loading performance using Chrome DevTools Protocol."""
        try:
            # Get page info
            response = requests.get(f'http://localhost:{port}/json/new')
            if response.status_code != 200:
                return {'success': False, 'error': 'Failed to create new page'}
            
            page_data = response.json()
            page_id = page_data['id']
            
            # Navigate to page
            navigate_cmd = {
                'id': 1,
                'method': 'Page.navigate',
                'params': {'url': url}
            }
            
            start_time = time.time()
            response = requests.post(
                f'http://localhost:{port}/json/protocol/{page_id}',
                json=navigate_cmd,
                timeout=30
            )
            
            if response.status_code != 200:
                return {'success': False, 'error': 'Navigation failed'}
            
            # Wait for page load
            load_time = self.wait_for_page_load(port, page_id)
            
            # Get page metrics
            metrics_cmd = {
                'id': 2,
                'method': 'Page.getMetrics',
                'params': {}
            }
            
            response = requests.post(
                f'http://localhost:{port}/json/protocol/{page_id}',
                json=metrics_cmd,
                timeout=10
            )
            
            metrics = {}
            if response.status_code == 200:
                metrics = response.json().get('result', {})
            
            # Close page
            requests.post(f'http://localhost:{port}/json/close/{page_id}')
            
            return {
                'success': True,
                'load_time': load_time,
                'total_time': time.time() - start_time,
                'metrics': metrics
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def wait_for_page_load(self, port: int, page_id: str, max_wait: int = 30) -> float:
        """Wait for page to load completely."""
        start_time = time.time()
        
        while time.time() - start_time < max_wait:
            try:
                response = requests.get(f'http://localhost:{port}/json/protocol/{page_id}')
                if response.status_code == 200:
                    data = response.json()
                    if data.get('result', {}).get('readyState') == 'complete':
                        return time.time() - start_time
            except:
                pass
            time.sleep(0.5)
        
        return max_wait
    
    def get_container_stats(self, name: str) -> Dict[str, Any]:
        """Get container resource usage statistics."""
        try:
            result = subprocess.run(
                ['docker', 'stats', '--no-stream', '--format', 'json', name],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0 and result.stdout.strip():
                stats = json.loads(result.stdout.strip())
                return {
                    'cpu_percent': float(stats.get('CPUPerc', '0%').rstrip('%')),
                    'memory_usage': stats.get('MemUsage', '0B'),
                    'memory_percent': float(stats.get('MemPerc', '0%').rstrip('%')),
                    'network_io': stats.get('NetIO', '0B'),
                    'block_io': stats.get('BlockIO', '0B')
                }
        except Exception as e:
            print(f"Error getting container stats: {e}")
        
        return {}
    
    def run_benchmark(self, image: str, name: str, port: int, test_urls: List[str]) -> Dict[str, Any]:
        """Run complete benchmark for a container."""
        print(f"\n=== Running benchmark for {image} ===")
        
        # Start container
        startup_result = self.start_container(image, name, port)
        
        if not startup_result['success']:
            print(f"Failed to start container {image}: {startup_result['stderr']}")
            return {
                'image': image,
                'success': False,
                'error': startup_result['stderr']
            }
        
        # Wait a bit for container to stabilize
        time.sleep(5)
        
        # Get initial stats
        initial_stats = self.get_container_stats(name)
        
        # Test page loads
        page_load_results = []
        for url in test_urls:
            print(f"Testing page load: {url}")
            result = self.test_page_load(port, url)
            page_load_results.append(result)
            time.sleep(2)  # Wait between tests
        
        # Get final stats
        final_stats = self.get_container_stats(name)
        
        # Stop container
        self.run_command(['docker', 'stop', name], timeout=10)
        
        return {
            'image': image,
            'success': True,
            'startup': startup_result,
            'page_loads': page_load_results,
            'initial_stats': initial_stats,
            'final_stats': final_stats,
            'test_urls': test_urls
        }
    
    def run_all_benchmarks(self, test_urls: List[str]) -> Dict[str, Any]:
        """Run benchmarks for all containers."""
        containers = [
            {
                'image': 'chromedp/headless-shell:latest',
                'name': 'benchmark-chromedp',
                'port': 9222
            },
            {
                'image': 'thorium-docker:avx2',
                'name': 'benchmark-thorium-avx2',
                'port': 9223
            },
            {
                'image': 'thorium-docker:avx',
                'name': 'benchmark-thorium-avx',
                'port': 9224
            },
            {
                'image': 'thorium-docker:sse3',
                'name': 'benchmark-thorium-sse3',
                'port': 9225
            },
            {
                'image': 'thorium-docker:sse4',
                'name': 'benchmark-thorium-sse4',
                'port': 9226
            }
        ]
        
        all_results = []
        
        for container in containers:
            try:
                result = self.run_benchmark(
                    container['image'],
                    container['name'],
                    container['port'],
                    test_urls
                )
                all_results.append(result)
            except Exception as e:
                print(f"Error benchmarking {container['image']}: {e}")
                all_results.append({
                    'image': container['image'],
                    'success': False,
                    'error': str(e)
                })
        
        return {
            'timestamp': datetime.now().isoformat(),
            'iterations': self.iterations,
            'test_urls': test_urls,
            'results': all_results
        }
    
    def generate_report(self, benchmark_results: Dict[str, Any]) -> str:
        """Generate a detailed performance report."""
        report = []
        report.append("# Thorium Docker Performance Benchmark Report")
        report.append(f"Generated: {benchmark_results['timestamp']}")
        report.append(f"Iterations: {benchmark_results['iterations']}")
        report.append("")
        
        # Summary table
        report.append("## Performance Summary")
        report.append("")
        report.append("| Container | Startup Time (s) | Avg Load Time (s) | Memory Usage | Success Rate |")
        report.append("|-----------|------------------|-------------------|--------------|--------------|")
        
        for result in benchmark_results['results']:
            if result['success']:
                startup_time = result['startup']['total_startup_time']
                
                # Calculate average load time
                load_times = [r['load_time'] for r in result['page_loads'] if r['success']]
                avg_load_time = statistics.mean(load_times) if load_times else 0
                
                memory_usage = result['final_stats'].get('memory_usage', 'N/A')
                success_rate = len([r for r in result['page_loads'] if r['success']]) / len(result['page_loads']) * 100
                
                report.append(f"| {result['image']} | {startup_time:.2f} | {avg_load_time:.2f} | {memory_usage} | {success_rate:.1f}% |")
            else:
                report.append(f"| {result['image']} | FAILED | FAILED | N/A | 0% |")
        
        report.append("")
        
        # Detailed results
        report.append("## Detailed Results")
        report.append("")
        
        for result in benchmark_results['results']:
            report.append(f"### {result['image']}")
            report.append("")
            
            if result['success']:
                report.append(f"**Startup Time**: {result['startup']['total_startup_time']:.2f}s")
                report.append(f"**Ready Time**: {result['startup']['ready_time']:.2f}s")
                report.append("")
                
                report.append("**Page Load Results**:")
                for i, page_result in enumerate(result['page_loads']):
                    url = result['test_urls'][i]
                    if page_result['success']:
                        report.append(f"- {url}: {page_result['load_time']:.2f}s")
                    else:
                        report.append(f"- {url}: FAILED ({page_result.get('error', 'Unknown error')})")
                
                report.append("")
                report.append("**Resource Usage**:")
                report.append(f"- CPU: {result['final_stats'].get('cpu_percent', 'N/A')}%")
                report.append(f"- Memory: {result['final_stats'].get('memory_usage', 'N/A')}")
                report.append(f"- Memory %: {result['final_stats'].get('memory_percent', 'N/A')}%")
            else:
                report.append(f"**Error**: {result.get('error', 'Unknown error')}")
            
            report.append("")
        
        return "\n".join(report)
    
    def save_results(self, benchmark_results: Dict[str, Any], filename: str = None):
        """Save benchmark results to file."""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"benchmark_results_{timestamp}.json"
        
        with open(filename, 'w') as f:
            json.dump(benchmark_results, f, indent=2)
        
        print(f"Results saved to: {filename}")
        return filename

def main():
    parser = argparse.ArgumentParser(description='Run performance benchmarks for Thorium Docker containers')
    parser.add_argument('--iterations', type=int, default=5, help='Number of iterations per test')
    parser.add_argument('--timeout', type=int, default=30, help='Timeout for operations in seconds')
    parser.add_argument('--urls', nargs='+', default=[
        'https://www.google.com',
        'https://www.github.com',
        'https://www.stackoverflow.com',
        'https://www.wikipedia.org'
    ], help='URLs to test')
    parser.add_argument('--output', help='Output file for results')
    parser.add_argument('--report', help='Output file for report')
    
    args = parser.parse_args()
    
    # Check if Docker is running
    try:
        subprocess.run(['docker', 'version'], check=True, capture_output=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("Error: Docker is not running or not installed")
        sys.exit(1)
    
    # Run benchmarks
    runner = BenchmarkRunner(iterations=args.iterations, timeout=args.timeout)
    
    print("Starting performance benchmarks...")
    print(f"Test URLs: {args.urls}")
    print(f"Iterations: {args.iterations}")
    print("")
    
    results = runner.run_all_benchmarks(args.urls)
    
    # Save results
    results_file = runner.save_results(results, args.output)
    
    # Generate and save report
    report = runner.generate_report(results)
    if args.report:
        with open(args.report, 'w') as f:
            f.write(report)
        print(f"Report saved to: {args.report}")
    else:
        print("\n" + "="*80)
        print(report)
    
    # Print summary
    print("\n" + "="*80)
    print("BENCHMARK SUMMARY")
    print("="*80)
    
    successful_results = [r for r in results['results'] if r['success']]
    if successful_results:
        fastest_startup = min(successful_results, key=lambda x: x['startup']['total_startup_time'])
        fastest_load = min(successful_results, key=lambda x: statistics.mean([r['load_time'] for r in x['page_loads'] if r['success']]))
        
        print(f"Fastest startup: {fastest_startup['image']} ({fastest_startup['startup']['total_startup_time']:.2f}s)")
        print(f"Fastest page load: {fastest_load['image']} ({statistics.mean([r['load_time'] for r in fastest_load['page_loads'] if r['success']]):.2f}s)")
    
    print(f"Results saved to: {results_file}")

if __name__ == "__main__":
    main() 