# Validating

## Overview

This document provides detailed instructions for deploying, launching, and reinitializing the validator project. It includes key steps like setting up the environment, running scripts, and using the PM2 ecosystem file for auto-update. **Important: Ensure that port 443 is open and available for secure HTTPS communication with the validator. All validator commands should be run from the `sudo -s` environment to avoid permission issues.**

## Table of Contents

1. [Deployment](#deployment)
    - [Cloning the Repository](#cloning-the-repository)
    - [Setting up the Virtual Environment](#setting-up-the-virtual-environment)
    - [Running the Build Script](#running-the-build-script)
2. [Launch](#launch)
    - [Running the Validator using the PM2 Ecosystem File](#running-the-validator-using-the-pm2-ecosystem-file)
3. [Subsequent Important Steps](#subsequent-important-steps)
4. [Reinitialization](#reinitialization)

## Deployment

### Cloning the Repository

To begin, clone the repository for the validator project:

```bash
git clone https://github.com/eseckft/BitAds.ai.git
cd BitAds.ai
```

### Setting up the Virtual Environment

After cloning the repository, create and activate a Python virtual environment to manage dependencies:

1. **Create a Virtual Environment**:
   Run the following command to create a virtual environment:

   ```bash
   python3 -m venv venv
   ```

2. **Activate the Virtual Environment**:
    - On Windows:

      ```bash
      .\venv\Scripts\activate
      ```

    - On macOS and Linux:

      ```bash
      source venv/bin/activate
      ```

3. **Switch to Root Environment**:
   After activating the virtual environment, switch to the root environment to avoid permission issues. Run:

   ```bash
   sudo -s
   ```

---

### Running the Build Script

Once in the root environment and still within the project directory, execute the build script to handle the setup. This script automates several key deployment steps, including:

- Downloading the Geo2Lite database for country detection
- Installing all necessary Python dependencies
- Setting up SQLite
- Generating a self-signed SSL certificate if one doesn't already exist

You need to provide your wallet name and hotkey, along with the `subtensor.network` as parameters when running the script. Here’s the command:

```bash
source ./build_project.sh --wallet.name <wallet_name> --wallet.hotkey <wallet_hotkey> --subtensor.network <network> --subtensor.chain_endpoint wss://entrypoint-finney.opentensor.ai:443
```

#### Parameters:
- `--wallet.name <wallet_name>`: The name of your wallet.
- `--wallet.hotkey <wallet_hotkey>`: The hotkey name associated with your wallet.
- `--subtensor.network <network>`: The Subtensor network to connect to (e.g., `finney`, `test`, etc.).
- `--subtensor.chain_endpoint <chain_endpoint>` (optional): The Subtensor chain endpoint to connect to. If not specified, it defaults to `wss://entrypoint-finney.opentensor.ai:443`.

For example:

```bash
source ./build_project.sh --wallet.name default --wallet.hotkey default --subtensor.network finney
```

The script handles all necessary setup steps, so you don't need to manually install dependencies, set up databases, or generate SSL certificates.

Once the build script completes, the system will be ready for the next steps in launching the validator using the PM2 ecosystem file.

### Create account on BitAds.ai (Mandatory)

Validator registration is required. This allows the server to ping, informing us of your activity so we can include it in the DNS records, ensuring the participant is accessible via x.bitads.ai or v.bitads.ai. <br><br>
Without an account, Validators won't be able to set weights on the subnet. Having an account gives Validators easy access to miner and campaign statistics, as well as the API key needed to build their own application on the BitAds subnet. <br><br>
Validators will be manually approved after we receive written confirmation on Discord regarding their registration.<br><br>
For any inquiries regarding script usage or registration, please refer to the official documentation on BitAds.ai or contact our support team.<br>
You can register here: [BitAds.ai](https://bitads.ai/register)

## Launch

### Running the Validator using the PM2 Ecosystem File

To run the validator and ensure it automatically updates, you will use the PM2 ecosystem configuration file, `validator-ecosystem.config.js`. PM2 will manage the validator process, keeping it running and ensuring it is up-to-date.

1. **Start the Validator using the Ecosystem File**:

   Run the following command to start the validator process via the PM2 ecosystem file:

   ```bash
   pm2 start validator-ecosystem.config.js
   ```

This ecosystem file contains all the necessary configurations, including auto-update functionality, so there's no need to manually run any separate update command. PM2 will handle process management and updates automatically.

For more information on PM2 ecosystem configuration, you can refer to the [PM2 documentation](https://pm2.keymetrics.io/docs/usage/application-declaration/).

---

## Subsequent Important Steps

1. **Monitor the Validator**:
   Use `pm2` to monitor the status of your validator process:

   ```bash
   pm2 status
   ```

2. **Handling Updates**:
   If you need to change wallet parameters or the chain endpoint, it's best to rebuild the project with the new parameters instead of using environment variable commands. You can run the build script again with the updated parameters, and then start or reload the PM2 process:

   For example, if you need to change the wallet:

   ```bash
   pm2 del validator-ecosystem.config.js  # stop previous processes (if env still active, else use pm2 list and del each process of previously running validator)
   source ./build_project.sh --wallet.name new_wallet_name --wallet.hotkey new_wallet_hotkey --subtensor.network finney
   pm2 startOrReload validator-ecosystem.config.js
   ```

3. **Logging and Debugging**:
   To check logs for issues or errors:

   ```bash
   pm2 logs
   ```

**Reminder:** Always ensure port 443 is open for secure communication, and run all commands within the `sudo su -` environment.

---

## Reinitialization

If you encounter critical issues during operation, refer to the [reinitialization process](reinitialization.md) instructions for troubleshooting and restarting the validator setup.

**Note:** Currently, the auto-update script supports only one running instance of the validator on the server; in the future, it will be able to run multiple instances.
