# Multi-stage build for Thorium headless browser
FROM debian:bullseye-slim AS base

# Install system dependencies for headless browser
RUN apt-get update && apt-get install -y \
    ca-certificates \
    fonts-liberation \
    libappindicator3-1 \
    libasound2 \
    libatk-bridge2.0-0 \
    libdrm2 \
    libgtk-3-0 \
    libnspr4 \
    libnss3 \
    libxcomposite1 \
    libxdamage1 \
    libxrandr2 \
    xdg-utils \
    libxss1 \
    libxtst6 \
    libx11-xcb1 \
    libxcb-dri3-0 \
    libdrm2 \
    libgbm1 \
    libasound2 \
    libatspi2.0-0 \
    libxshmfence1 \
    fonts-noto-cjk \
    fonts-noto-cjk-extra \
    fonts-noto-color-emoji \
    fonts-dejavu-core \
    fonts-liberation \
    locales \
    && rm -rf /var/lib/apt/lists/*

# Set locale for proper character encoding
RUN locale-gen en_US.UTF-8
ENV LANG=en_US.UTF-8
ENV LANGUAGE=en_US:en
ENV LC_ALL=en_US.UTF-8

# Create non-root user for security
RUN groupadd -r thorium && useradd -r -g thorium -G audio,video thorium \
    && mkdir -p /home/thorium /config \
    && chown -R thorium:thorium /home/thorium /config

# Thorium installation stage
FROM base AS thorium-install

# Switch back to root for installation
USER root

# Install additional dependencies for Thorium
RUN apt-get update && apt-get install -y \
    wget \
    dpkg \
    && rm -rf /var/lib/apt/lists/*

# Set Thorium version and instruction set
ARG THORIUM_VERSION=M130.0.6723.174
ARG INSTRUCTION_SET=AVX2
ENV THORIUM_VERSION=${THORIUM_VERSION}
ENV INSTRUCTION_SET=${INSTRUCTION_SET}

# Define download URL based on instruction set
RUN case "${INSTRUCTION_SET}" in \
        "AVX2") \
            THORIUM_DEB_URL="https://github.com/Alex313031/thorium/releases/download/${THORIUM_VERSION}/thorium_${THORIUM_VERSION}_amd64_AVX2.deb" \
            ;; \
        "AVX") \
            THORIUM_DEB_URL="https://github.com/Alex313031/thorium/releases/download/${THORIUM_VERSION}/thorium_${THORIUM_VERSION}_amd64_AVX.deb" \
            ;; \
        "SSE3") \
            THORIUM_DEB_URL="https://github.com/Alex313031/thorium/releases/download/${THORIUM_VERSION}/thorium_${THORIUM_VERSION}_amd64_SSE3.deb" \
            ;; \
        "SSE4") \
            THORIUM_DEB_URL="https://github.com/Alex313031/thorium/releases/download/${THORIUM_VERSION}/thorium_${THORIUM_VERSION}_amd64_SSE4.deb" \
            ;; \
        *) \
            echo "Unsupported instruction set: ${INSTRUCTION_SET}" && exit 1 \
            ;; \
    esac && \
    echo "Downloading Thorium ${THORIUM_VERSION} for ${INSTRUCTION_SET}..." && \
    echo "URL: ${THORIUM_DEB_URL}" && \
    wget -q "${THORIUM_DEB_URL}" -O thorium.deb && \
    if [ ! -f thorium.deb ] || [ ! -s thorium.deb ]; then \
        echo "Error: Failed to download Thorium package" && \
        echo "Trying alternative URL format..." && \
        wget -q "https://github.com/Alex313031/thorium/releases/download/${THORIUM_VERSION}/thorium-browser_${THORIUM_VERSION}_${INSTRUCTION_SET}.deb" -O thorium.deb && \
        if [ ! -f thorium.deb ] || [ ! -s thorium.deb ]; then \
            echo "Error: Failed to download Thorium package with alternative format" && \
            exit 1; \
        fi; \
    fi && \
    echo "Download successful, installing..." && \
    dpkg -i thorium.deb || true && \
    apt-get update && apt-get install -f -y && \
    rm thorium.deb && \
    rm -rf /var/lib/apt/lists/*

# Create symlink for easier access and verify installation
RUN echo "Checking thorium installation..." && \
    ls -la /usr/bin/thorium* || echo "No thorium files found yet" && \
    echo "Creating symlink..." && \
    ln -sf /usr/bin/thorium-browser /usr/bin/thorium && \
    echo "Checking if thorium-browser exists..." && \
    if [ -f /usr/bin/thorium-browser ]; then \
        echo "thorium-browser found, checking version..." && \
        /usr/bin/thorium-browser --version; \
    else \
        echo "Error: thorium-browser not found in /usr/bin/" && \
        echo "Checking what was installed..." && \
        dpkg -l | grep thorium && \
        find /usr -name "*thorium*" 2>/dev/null && \
        exit 1; \
    fi && \
    echo "Verifying thorium symlink..." && \
    if [ -L /usr/bin/thorium ]; then \
        echo "Symlink created successfully" && \
        /usr/bin/thorium --version; \
    else \
        echo "Error: Symlink creation failed" && \
        exit 1; \
    fi

# Add instruction set info to container
RUN echo "Thorium ${THORIUM_VERSION} built for ${INSTRUCTION_SET}" > /etc/thorium-info.txt

# Switch back to thorium user
USER thorium

# Final stage
FROM thorium-install

# Set working directory
WORKDIR /home/thorium

# Switch to non-root user
USER thorium

# Expose port for remote debugging
EXPOSE 9222

# Default command for headless mode
CMD ["/usr/bin/thorium", "--headless", "--disable-gpu", "--no-sandbox", "--disable-dev-shm-usage", "--remote-debugging-port=9222", "--disable-web-security", "--disable-features=VizDisplayCompositor"] 