# Validating

## Overview

This document provides detailed instructions for deploying, launching, and reinitializing the validator project. It includes key steps like setting up the environment, running scripts, and using the PM2 ecosystem file for auto-update. **Important: Ensure that port 443 is open and available for secure HTTPS communication with the validator. All validator commands should be run from the `sudo su -` environment to avoid permission issues.**

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
   sudo su -
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
./build_project --wallet.name <wallet_name> --wallet.hotkey <wallet_hotkey> --subtensor.network <network>
```

#### Parameters:
- `--wallet.name <wallet_name>`: The name of your wallet.
- `--wallet.hotkey <wallet_hotkey>`: The hotkey name associated with your wallet.
- `--subtensor.network <network>`: The Subtensor network to connect to (e.g., `finney`, `test`, etc.).

For example:

```bash
./build_project.sh --wallet.name default --wallet.hotkey default --subtensor.network finney
```

The script handles all necessary setup steps, so you don't need to manually install dependencies, set up databases, or generate SSL certificates.

Once the build script completes, the system will be ready for the next steps in launching the validator using the PM2 ecosystem file.

---

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
   The PM2 ecosystem file ensures that the validator automatically handles updates. No additional steps are required to manage updates manually.

3. **Restarting Processes**:
   If necessary, manually restart the validator processes using `pm2`:

   ```bash
   pm2 restart validator_server_<wallet_hotkey>
   pm2 restart validator_proxy_server_<wallet_hotkey>
   ```

4. **Logging and Debugging**:
   To check logs for issues or errors:

   ```bash
   pm2 logs
   ```

**Reminder:** Always ensure port 443 is open for secure communication, and run all commands within the `sudo su -` environment.

---

## Reinitialization

If you encounter critical issues during operation, refer to the [reinitialization process](reinitialization.md) instructions for troubleshooting and restarting the validator setup.
