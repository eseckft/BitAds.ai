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
3. [Updating Environment Variables](#updating-environment-variables)
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

1. **Install Python 3.11+**:

   Ensure that Python 3.11+ is installed on your system. You can download it from
   the [official Python website](https://www.python.org/downloads/).


2. **Create a Virtual Environment**:
   Run the following command to create a virtual environment:

   ```bash
   python3 -m venv venv
   ```

3. **Switch to Root Environment**:
   After activating the virtual environment, switch to the root environment to avoid permission issues. Run:

   ```bash
   sudo -s
   ```

4. **Activate the Virtual Environment**:
    - On Windows:

      ```bash
      .\venv\Scripts\activate
      ```

    - On macOS and Linux:

      ```bash
      source venv/bin/activate
      ```

---

### Running the Build Script

Once in the root environment and still within the project directory, execute the build script to handle the setup. This script automates several key deployment steps, including:

- Downloading the Geo2Lite database for country detection
- Installing all necessary Python dependencies
- Setting up SQLite
- Generating a self-signed SSL certificate if one doesn't already exist

You need to provide your wallet name, hotkey, and the `subtensor.network` as parameters when running the script. Additionally, you can specify the type of neuron (either `miner` or `validator`). Here’s the command:

```bash
./build_project.sh --wallet.name <wallet_name> --wallet.hotkey <wallet_hotkey> --subtensor.network <network> --subtensor.chain_endpoint <chain_endpoint> --neuron.type <neuron_type>
```

#### Parameters:
- `--wallet.name <wallet_name>`: The name of your wallet.
- `--wallet.hotkey <wallet_hotkey>`: The hotkey name associated with your wallet.
- `--subtensor.network <network>`: The Subtensor network to connect to (e.g., `finney`, `test`, etc.).
- `--subtensor.chain_endpoint <chain_endpoint>` (optional): The Subtensor chain endpoint to connect to. If not specified, it defaults to `wss://entrypoint-finney.opentensor.ai:443`.
- `--neuron.type <neuron_type>`: The type of neuron to use, either `miner` or `validator`.

For example:

```bash
./build_project.sh --wallet.name default --wallet.hotkey default --subtensor.network finney --neuron.type validator
```

Once the build script completes, the system will be ready for the next steps in launching the validator using the PM2 ecosystem file.


### Create account on BitAds.ai (Optional)

Registration is no longer necessary for validators. However, you can still create an account to conveniently view statistics and access other platform features.

Having an account provides users with easy access to miner and campaign statistics, as well as the API key needed to build their own applications on the BitAds subnet.

If you wish to register for additional features, you can do so here: [BitAds.ai](https://bitads.ai/sign-up)


#### Receiving 2FA Codes

Once the full application setup is complete and the proxy is operational (you should see the following log message:

```
Uvicorn running on https://0.0.0.0:443 (Press CTRL+C to quit)
```

), you can retrieve your 2FA codes for registration by running the following command:

```bash
bacli 2fa list
```

**If you encounter the error `command not found: bacli`:**

1. **Ensure the Virtual Environment is Activated**:

   Make sure that your virtual environment is active. If not, activate it using:

   - On Windows:

     ```bash
     .\venv\Scripts\activate
     ```

   - On macOS and Linux:

     ```bash
     source venv/bin/activate
     ```

2. **Install the Package Locally**:

   Run the following command to install the necessary package:

   ```bash
   pip install .
   ```

   After successful installation, retry the `bacli 2fa list` command.


## Launch

To ensure that the `validator_proxy` has started correctly, you can include a step in the documentation that verifies the presence of the log message:

```
INFO:     Uvicorn running on https://0.0.0.0:443 (Press CTRL+C to quit)
```

This log indicates that Uvicorn, the ASGI server, is running successfully on port 443. Here's how you can update the documentation to check for this log message:

---

## Launch

### Running the Validator using the PM2 Ecosystem File

To run the validator and ensure it automatically updates, you will use the PM2 ecosystem configuration file, `validator-ecosystem.config.js`. PM2 will manage the validator process, keeping it running and ensuring it is up-to-date.

1. **Start the Validator using the Ecosystem File**:

   Run the following command to start the validator process via the PM2 ecosystem file:

   ```bash
   export $(cat .env | xargs) && pm2 start validator-ecosystem.config.js
   ```

   This ecosystem file contains all the necessary configurations, including auto-update functionality, so there's no need to manually run any separate update command. PM2 will handle process management and updates automatically.

2. **Ensure `validator_proxy` is Running Correctly**:

   After starting the validator, it's critical to verify that the `validator_proxy` service has started successfully, as it directly affects the operation of the VTrust mechanism.

   To check the status of `validator_proxy`, run the following command:

   ```bash
   pm2 status validator_proxy_$WALLET_HOTKEY
   ```

   Ensure that its status is listed as `online`. If the status is different (e.g., `stopped` or `errored`), troubleshoot immediately to avoid impacting VTrust.

3. **Verify Uvicorn is Running**:

   To further confirm that the `validator_proxy` is functioning correctly, check the logs to see the following message, which indicates that Uvicorn is running on the expected port (443):

   ```bash
   pm2 logs validator_proxy_$WALLET_HOTKEY
   ```

   Look for the log entry:

   ```
   INFO:     Uvicorn running on https://0.0.0.0:443 (Press CTRL+C to quit)
   ```

   If this log is not present, Uvicorn might not have started correctly, and you should investigate further.


For more information on PM2 ecosystem configuration, you can refer to the [PM2 documentation](https://pm2.keymetrics.io/docs/usage/application-declaration/).

---

## Updating Environment Variables

If you need to change any environment variables (like wallet information or Subtensor settings), follow these steps:

1. **Stop the Validator**:
   Delete the running validator process to reset the environment:

   ```bash
   export $(cat .env | xargs) && pm2 del validator-ecosystem.config.js
   ```

2. **Edit the Environment Variables**:
   Open the `.env` file using an editor like `nano` or `vim`:

   ```bash
   nano .env
   ```

   Make your changes and save the file.

3. **Restart the Validator**:
   After updating the `.env` file, restart the validator:

   ```bash
   export $(cat .env | xargs) && pm2 start validator-ecosystem.config.js
   ```

This will apply the new environment variables and ensure the validator runs with updated configurations.

---

## Reinitialization

If you encounter critical issues during operation, refer to the [reinitialization process](reinitialization.md) instructions for troubleshooting and restarting the validator setup.

**Note:** Currently, the auto-update script supports only one running instance of the validator on the server; in the future, it will be able to run multiple instances.
