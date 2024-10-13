#!/bin/bash

# Default value for restart_proxy
restart_proxy=false
subtensor_network=finney
log_file=~/.bittensor/miners/bittensor.log
prefix="Auto-update script |"

# Store the remaining arguments in an array
args=("$@")

# Loop through command-line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --wallet.hotkey)
            # Move to the value of --wallet.hotkey
            shift
            wallet_hotkey="$1" # Assign the value to wallet_hotkey
            ;;
        --wallet.name)
            # Move to the value of --wallet.hotkey
            shift
            wallet_name="$1" # Assign the value to wallet_hotkey
            ;;
        --restart-proxy)
            restart_proxy=true
            ;;
        --subtensor.network)
            shift
            subtensor_network="$1"
            ;;
    esac
    shift # Move to the next argument
done

# Set the remaining arguments back
set -- "${args[@]}"

# Check if wallet hotkey is empty
if [ -z "$wallet_hotkey" ]; then
    echo "$prefix Error: Wallet hotkey not provided. Exiting..." | tee -a "$log_file"
    exit 1
fi

export SUBTENSOR_NETWORK=$subtensor_network
export WALLET_NAME=$wallet_name
export WALLET_HOTKEY=$wallet_hotkey
export NEURON_TYPE=validator

echo "$prefix Installing dependencies..." | tee -a "$log_file"
python3 -m pip install -r requirements.txt

# python3 -m pip install --upgrade bittensor
python3 -m pip install -e .
python3 setup.py install_lib
python3 setup.py build
python3 get_databases.py
alembic upgrade head

# Check if the process is currently managed by PM2
pm2_status=$(pm2 list | grep -c "validator_server_$wallet_hotkey")

if [ $pm2_status -gt 0 ]; then
    # If the process is running, delete it
    pm2 delete validator_server_$wallet_hotkey
    echo "$prefix Process deleted from PM2." | tee -a "$log_file"
else
    echo "$prefix Process is not currently managed by PM2." | tee -a "$log_file"
fi

if [ "$restart_proxy" = true ]; then
    echo "$prefix Restarting proxy..." | tee -a "$log_file"
    # Add commands to restart the proxy here
    pm2_status=$(pm2 list | grep -c "validator_proxy_server_$wallet_hotkey")

    if [ $pm2_status -gt 0 ]; then
        # If the process is running, delete it
        pm2 delete validator_proxy_server_$wallet_hotkey
        echo "$prefix Proxy process deleted from PM2." | tee -a "$log_file"
    else
        echo "$prefix Proxy process is not currently managed by PM2." | tee -a "$log_file"
    fi

    pm2 start --name validator_proxy_server_$wallet_hotkey proxies/validator.py --interpreter python3 -- $@ | tee -a "$log_file"
fi

pm2 start --name validator_server_$wallet_hotkey neurons/validator/core.py --interpreter python3 -- $@ | tee -a "$log_file"