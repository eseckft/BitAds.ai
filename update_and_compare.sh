#!/bin/bash

# Step 1: Change to the directory of the script
cd "$(dirname "${BASH_SOURCE[0]}")" || exit 1  # Exit if the cd fails

# Step 2: Fetch updates from GitHub
echo "Fetching updates from GitHub..."
git pull

# Define temporary files to store results
RUNNING_CORE_VERSION_FILE="tmp/running_core_version.txt"
LOCAL_CORE_VERSION_FILE="tmp/local_core_version.txt"
RUNNING_PROXY_VERSION_FILE="tmp/running_proxy_version.txt"
LOCAL_PROXY_VERSION_FILE="tmp/local_proxy_version.txt"

# Create a temporary directory if it doesn't exist
mkdir -p tmp

# Step 3: Fetch versions in parallel

# Fetch core versions (container and local) in background
{
    echo "Checking version in running container for the core service..."
    RUNNING_CORE_VERSION=$(docker compose exec core python -c "import neurons; print(neurons.__version__)")
    echo "$RUNNING_CORE_VERSION" > "$RUNNING_CORE_VERSION_FILE"
} &

{
    echo "Checking version in updated local code for the core service..."
    LOCAL_CORE_VERSION=$(python -c "import neurons; print(neurons.__version__)")
    echo "$LOCAL_CORE_VERSION" > "$LOCAL_CORE_VERSION_FILE"
} &

# Fetch proxy versions (container and local) in background
{
    echo "Checking version in running container for the proxy service..."
    RUNNING_PROXY_VERSION=$(docker compose exec proxy bash get_proxy_version.sh)
    echo "$RUNNING_PROXY_VERSION" > "$RUNNING_PROXY_VERSION_FILE"
} &

{
    echo "Checking version in updated local code for the proxy service..."
    LOCAL_PROXY_VERSION=$(bash get_proxy_version.sh)
    echo "$LOCAL_PROXY_VERSION" > "$LOCAL_PROXY_VERSION_FILE"
} &

# Wait for all background processes to finish
wait

# Read the results from temporary files
RUNNING_CORE_VERSION=$(cat "$RUNNING_CORE_VERSION_FILE")
LOCAL_CORE_VERSION=$(cat "$LOCAL_CORE_VERSION_FILE")
RUNNING_PROXY_VERSION=$(cat "$RUNNING_PROXY_VERSION_FILE")
LOCAL_PROXY_VERSION=$(cat "$LOCAL_PROXY_VERSION_FILE")

# Clean up temporary files
rm "$RUNNING_CORE_VERSION_FILE" "$LOCAL_CORE_VERSION_FILE" "$RUNNING_PROXY_VERSION_FILE" "$LOCAL_PROXY_VERSION_FILE"

# Step 4: Compare versions and rebuild if necessary

# Core service version comparison
if [ "$RUNNING_CORE_VERSION" != "$LOCAL_CORE_VERSION" ]; then
    echo "Version mismatch detected for the core service. Rebuilding and restarting the 'core' service..."
    docker compose up -d core --build
    echo "'core' service has been rebuilt and restarted."
else
    echo "Versions of cores are the same. No rebuild required."
fi

# Proxy service version comparison
if [ "$RUNNING_PROXY_VERSION" != "$LOCAL_PROXY_VERSION" ]; then
    echo "Version mismatch detected for the proxy service. Rebuilding and restarting the 'proxy' service..."
    docker compose up -d proxy --build
    echo "'proxy' service has been rebuilt and restarted."
else
    echo "Versions of proxies are the same. No rebuild required."
fi