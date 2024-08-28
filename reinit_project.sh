#!/bin/bash

# Default value for restart_proxy
subtensor_network=finney

# Store the remaining arguments in an array
args=("$@")

# Loop through command-line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --subtensor.network)
            # Move to the value of --wallet.hotkey
            shift
            subtensor_network="$1" # Assign the value to wallet_hotkey
            ;;
    esac
    shift # Move to the next argument
done

# Set the remaining arguments back
set -- "${args[@]}"

export SUBTENSOR_NETWORK=$subtensor_network

rm miner_active_${subtensor_network}.db
rm miner_history_${subtensor_network}.db
rm validator_active_${subtensor_network}.db
rm validator_history_${subtensor_network}.db
rm main_${subtensor_network}.db

alembic upgrade head