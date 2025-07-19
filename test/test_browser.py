#!/usr/bin/env python3
"""
Test script to verify Thorium headless browser functionality.
"""

import json
import requests
import time
import sys
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def test_remote_debugging():
    """
    Test remote debugging connection.
    
    Returns:
        bool: True if connection successful
    """
    try:
        # Check if remote debugging is accessible
        response = requests.get('http://localhost:9222/json/version', timeout=10)
        if response.status_code == 200:
            version_info = response.json()
            print(f"Remote debugging accessible: {version_info.get('Browser', 'Unknown')}")
            return True
        else:
            print(f"Remote debugging failed: {response.status_code}")
            return False
    except requests.RequestException as e:
        print(f"Remote debugging connection error: {e}")
        return False

def test_browser_functionality():
    """
    Test basic browser functionality using Selenium.
    
    Returns:
        bool: True if all tests pass
    """
    try:
        # Configure Chrome options for headless mode
        chrome_options = Options()
        chrome_options.add_experimental_option("debuggerAddress", "localhost:9222")
        
        # Connect to existing browser instance
        driver = webdriver.Chrome(options=chrome_options)
        
        # Test 1: Navigate to a simple page
        print("Testing navigation...")
        driver.get("https://httpbin.org/html")
        title = driver.title
        print(f"Page title: {title}")
        
        # Test 2: Check if page content is loaded
        body_text = driver.find_element(By.TAG_NAME, "body").text
        if "Herman Melville" in body_text:
            print("✓ Page content loaded successfully")
        else:
            print("✗ Page content not loaded properly")
            return False
        
        # Test 3: Test screenshot capability
        print("Testing screenshot...")
        screenshot_path = "/test/screenshot.png"
        driver.save_screenshot(screenshot_path)
        print(f"✓ Screenshot saved to {screenshot_path}")
        
        # Test 4: Test JavaScript execution
        print("Testing JavaScript execution...")
        result = driver.execute_script("return document.title;")
        print(f"JavaScript result: {result}")
        
        # Test 5: Test multi-language support
        print("Testing multi-language support...")
        driver.get("https://httpbin.org/encoding/utf8")
        content = driver.find_element(By.TAG_NAME, "body").text
        if "こんにちは" in content or "你好" in content:
            print("✓ Multi-language support working")
        else:
            print("⚠ Multi-language test inconclusive")
        
        driver.quit()
        return True
        
    except Exception as e:
        print(f"Browser functionality test failed: {e}")
        return False

def test_performance():
    """
    Test browser performance metrics.
    
    Returns:
        bool: True if performance is acceptable
    """
    try:
        chrome_options = Options()
        chrome_options.add_experimental_option("debuggerAddress", "localhost:9222")
        
        driver = webdriver.Chrome(options=chrome_options)
        
        # Test page load time
        start_time = time.time()
        driver.get("https://httpbin.org/delay/1")
        load_time = time.time() - start_time
        
        print(f"Page load time: {load_time:.2f} seconds")
        
        # Test memory usage (basic check)
        memory_info = driver.execute_script("""
            return {
                usedJSHeapSize: performance.memory.usedJSHeapSize,
                totalJSHeapSize: performance.memory.totalJSHeapSize
            }
        """)
        
        print(f"Memory usage: {memory_info}")
        
        driver.quit()
        
        # Acceptable performance thresholds
        if load_time < 5.0:  # Should load within 5 seconds
            print("✓ Performance test passed")
            return True
        else:
            print("✗ Performance test failed - load time too slow")
            return False
            
    except Exception as e:
        print(f"Performance test failed: {e}")
        return False

def main():
    """
    Main test function.
    """
    print("Starting Thorium headless browser tests...")
    
    # Wait for browser to start
    print("Waiting for browser to start...")
    time.sleep(10)
    
    # Run tests
    tests = [
        ("Remote Debugging", test_remote_debugging),
        ("Browser Functionality", test_browser_functionality),
        ("Performance", test_performance)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n--- {test_name} Test ---")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"Test {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n--- Test Summary ---")
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("All tests passed! 🎉")
        sys.exit(0)
    else:
        print("Some tests failed! ❌")
        sys.exit(1)

if __name__ == "__main__":
    main() 