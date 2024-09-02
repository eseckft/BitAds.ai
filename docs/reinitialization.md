# Reinitialization Script Documentation

## Overview

The [`reinit_project.sh`](../reinit_project.sh) script is designed to reinitialize the state of a project by performing
the following actions:

1. Parsing command-line arguments to determine the `subtensor.network`.
2. Setting environment variables.
3. Removing specific database files related to the provided `subtensor.network`.
4. Running database migrations using `alembic`.

## Usage

### Basic Command

```bash
./reinit_project.sh [options]
```

### Options

- `--subtensor.network <network_name>`: Specifies the name of the `subtensor.network`. If not provided, it defaults
  to `finney`.

## Detailed Description

1. **Default Value for `subtensor.network`**
    - The script initializes the `subtensor_network` variable with the default value `finney`.

   ```bash
   subtensor_network=finney
   ```

2. **Parsing Command-Line Arguments**
    - The script loops through the command-line arguments to find the `--subtensor.network` option and assigns its value
      to the `subtensor_network` variable.

   ```bash
   while [[ $# -gt 0 ]]; do
       case $1 in
           --subtensor.network)
               shift
               subtensor_network="$1"
               ;;
       esac
       shift
   done
   ```

3. **Setting Environment Variables**
    - The script sets the `SUBTENSOR_NETWORK` environment variable to the value of `subtensor_network`.

   ```bash
   export SUBTENSOR_NETWORK=$subtensor_network
   ```

4. **Removing Database Files**
    - The script removes database files associated with the specified `subtensor_network`.

   ```bash
   rm miner_active_${subtensor_network}.db
   rm miner_history_${subtensor_network}.db
   rm validator_active_${subtensor_network}.db
   rm validator_history_${subtensor_network}.db
   rm main_${subtensor_network}.db
   ```

5. **Running Database Migrations**
    - The script executes the `alembic upgrade head` command to apply database migrations.

   ```bash
   alembic upgrade head
   ```

## Examples

### Reinitialize with Default Network

To reinitialize the project with the default `finney` network:

```bash
./reinit_project.sh
```

### Reinitialize with a Specific Network

To reinitialize the project with a specific `subtensor.network` (e.g., `test`):

```bash
./reinit_project.sh --subtensor.network mainnet
```

This command sets the `subtensor.network` to `mainnet` and performs the reinitialization steps for that network.

## Notes

- Ensure that you have the necessary permissions to delete the database files and run the `alembic` commands.
- This script will delete the specified database files permanently. Make sure to back up any important data before
  running the script.

