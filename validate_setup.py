# validate_setup.py
import os
import sys

# Check if all necessary environment variables are set
required_vars = ["SUBTENSOR_NETWORK", "WALLET_NAME", "WALLET_HOTKEY", "AXON_PORT", "NEURON_TYPE"]

for var in required_vars:
    if not os.getenv(var):
        print(f"Error: Required environment variable {var} is not set.")
        sys.exit(1)  # Exit with an error code

# Additional validation logic can go here

print("All required environment variables are set.")