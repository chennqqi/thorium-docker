#!/bin/bash

# Test script for wrapped-thorium
echo "Testing wrapped-thorium script..."

# Check if wrapper script exists
if [ -f /usr/bin/wrapped-thorium ]; then
    echo "✅ wrapped-thorium script found"
    echo "Script permissions: $(ls -la /usr/bin/wrapped-thorium)"
else
    echo "❌ wrapped-thorium script not found"
    exit 1
fi

# Check if main binary exists
if [ -f /opt/chromium.org/thorium/thorium-browser ]; then
    echo "✅ thorium-browser binary found"
else
    echo "❌ thorium-browser binary not found"
    exit 1
fi

# Test version command
echo "Testing version command..."
if /usr/bin/wrapped-thorium --version > /dev/null 2>&1; then
    echo "✅ Version command works"
else
    echo "❌ Version command failed"
fi

# Test help command
echo "Testing help command..."
if /usr/bin/wrapped-thorium --help > /dev/null 2>&1; then
    echo "✅ Help command works"
else
    echo "❌ Help command failed"
fi

echo "Wrapper script test completed" 