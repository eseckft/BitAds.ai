#!/bin/bash

# Load environment variables from the .env file
set -o allexport
source .env
set +o allexport  # Corrected this line

# Run the Python command with the loaded environment variables
python3 -c "
import proxies
import os

# Access the NEURON_TYPE environment variable
NEURON_TYPE=os.getenv('NEURON_TYPE')

# Print the version of the corresponding neuron type
print(getattr(proxies, f'__{NEURON_TYPE}_version__'))
"