#!/bin/bash

# Record the start time
start_time=$(date +%s)

# Default values
subtensor_network=finney
subtensor_chain_endpoint=wss://entrypoint-finney.opentensor.ai:443

# Store the remaining arguments in an array
args=("$@")

# Loop through command-line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --wallet.hotkey)
            shift
            wallet_hotkey="$1"
            ;;
        --wallet.name)
            shift
            wallet_name="$1"
            ;;
        --subtensor.network)
            shift
            subtensor_network="$1"
            ;;
        --subtensor.chain_endpoint)
            shift
            subtensor_chain_endpoint="$1"
            ;;
        --neuron.type)
            shift
            neuron_type="$1"
            ;;
    esac
    shift
done

# Set the remaining arguments back
set -- "${args[@]}"

# Check if wallet hotkey is empty
if [ -z "$wallet_hotkey" ]; then
    echo "Error: Wallet hotkey not provided. Exiting..."
    exit 1
fi

# Check if neuron type is empty
if [ -z "$neuron_type" ]; then
    echo "Error: Neuron type is not provided. Exiting..."
    exit 1
fi

# Export environment variables
export SUBTENSOR_NETWORK=$subtensor_network
export SUBTENSOR_CHAIN_ENDPOINT=$subtensor_chain_endpoint
export WALLET_NAME=$wallet_name
export WALLET_HOTKEY=$wallet_hotkey
export NEURON_TYPE=$neuron_type

# Write the variables to .env file
echo "Writing environment variables to .env file..."
cat <<EOF > .env
SUBTENSOR_NETWORK=$subtensor_network
SUBTENSOR_CHAIN_ENDPOINT=$subtensor_chain_endpoint
WALLET_HOTKEY=$wallet_hotkey
WALLET_NAME=$wallet_name
NEURON_TYPE=$neuron_type
EOF

echo ".env file created successfully."

# Generate a self-signed certificate if it doesn't exist
if [ ! -f "key.pem" ] || [ ! -f "cert.pem" ]; then
    echo "Generating self-signed SSL certificate..."
    openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout key.pem \
        -out cert.pem \
        -subj "/C=US/ST=State/L=City/O=Bitads/CN=localhost"
else
    echo "SSL certificate already exists. Skipping generation."
fi

# Download the GeoLite2 database for country detection quietly
echo "Downloading GeoLite2-Country database..."
wget -q -O GeoLite2-Country.mmdb https://git.io/GeoLite2-Country.mmdb

# Install Python dependencies quietly
echo "Installing Python dependencies..."
pip3 install --upgrade pip -q
python3 -m pip install -r requirements.txt -q
python3 -m pip install . -q
python3 setup.py install_lib > /dev/null 2>&1
python3 setup.py build > /dev/null 2>&1

# Run the database update quietly
echo "Updating databases..."
python3 get_databases.py > /dev/null 2>&1
alembic upgrade head > /dev/null 2>&1

# Calculate and print the total execution time
end_time=$(date +%s)
execution_time=$((end_time - start_time))
echo "Script executed in $execution_time seconds."