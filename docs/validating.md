# Validating

## Overview

This document provides detailed instructions for deploying, launching, reinitializing, and performing subsequent
important steps for the validator project. The steps include setting up the environment, running the validator scripts,
and using the auto-update feature.

## Table of Contents

1. [Deployment](#deployment)
    - [Creating a Virtual Environment](#creating-a-virtual-environment)
    - [Installing Dependencies](#installing-dependencies)
2. [Country Detection](#country-detection)
3. [Launch](#launch)
    - [Running the Validator with Auto-Update](#running-the-validator-with-auto-update)
    - [Starting the Auto-Update for Landings](#starting-the-auto-update-for-landings)
    - [Example Command](#example-command)
4. [Subsequent Important Steps](#subsequent-important-steps)
5. [Reinitialization](#reinitialization)

## Deployment

### Creating a Virtual Environment

Creating a virtual environment is an optional but recommended step to manage dependencies and isolate the project
environment. The required Python version is 3.11+.

1. **Install Python 3.11+**:
   Ensure that Python 3.11+ is installed on your system. You can download it from
   the [official Python website](https://www.python.org/downloads/).

2. **Create a Virtual Environment**:
   Open a terminal and navigate to your project directory. Run the following command to create a virtual environment:

   ```bash
   python3 -m venv venv
   ```

3. **Activate the Virtual Environment**:
    - On Windows:

      ```bash
      .\venv\Scripts\activate
      ```

    - On macOS and Linux:

      ```bash
      source venv/bin/activate
      ```

### Country Detection

Download the Geo2Lite database, which is required for the project to detect and store the country information of IP
addresses:

```bash
wget https://git.io/GeoLite2-Country.mmdb
```

### Installing Dependencies

1. **Upgrade `pip`**:

   ```bash
   python3 -m pip install --upgrade pip
   ```

2. **Install Required Packages**:

   Run the following commands to install the required dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. **Install pm2**

   Installation instructions can be found [here](https://pm2.io/docs/runtime/guide/installation/)

4. **Install unzip**

   ```bash
   apt install unzip
   ```

## Launch

### Running the Validator with Auto-Update

The `run_validator_auto_update.py` script is used to launch the validator with an auto-update feature. This script
ensures that the local repository is always up-to-date with the remote repository and restarts the validator if
necessary.

### Starting the Auto-Update for Landings

To automatically load necessary landings and unzip them, you can use the `update_landings.sh` script with `pm2`. This
script will periodically download the latest landings and update the `statics` directory.

```bash
pm2 start update_landings.sh --name auto_update_landings --cron-restart="* * * * *" --no-autorestart
```

This script will automatically load necessary landings and unzip them.

### Generating a Self-Signed SSL Certificate

To secure the communication for your validator server, you may need to generate a self-signed SSL certificate. This can
be done using OpenSSL. Follow the steps below to create the certificate and key files:

```bash
openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout key.pem \
    -out cert.pem \
    -subj "/C=US/ST=State/L=City/O=Bitads/CN=localhost"
```

### Example Command

To run the validator with auto-update, use the following command:

```bash
pm2 start run_validator_auto_update.py --interpreter python3 -- --subtensor.network local --wallet.name <name> --wallet.hotkey <name>
```

- Replace `<name>` with your wallet name and hotkey.
- This command uses `pm2` to manage the process, ensuring it stays running and is easily restartable.

## Subsequent Important Steps

1. **Monitor the Validator**:
   Use `pm2` to monitor the status of your validator process. For example:

   ```bash
   pm2 status
   ```

2. **Handling Updates**:
   The `run_validator_auto_update.py` script automatically handles updates. Ensure that it is running correctly to keep
   your validator up-to-date.

3. **Restarting Processes**:
   If necessary, you can manually restart the validator or proxy processes using `pm2`. For example:

   ```bash
   pm2 restart validator_server_<wallet_hotkey>
   pm2 restart validator_proxy_server_<wallet_hotkey>
   ```

4. **Logging and Debugging**:
   Check the logs for any issues or errors:

   ```bash
   pm2 logs
   ```

By following these steps, you can successfully deploy, launch, and maintain your validator project. Continually update
this document as needed to reflect any changes or new procedures.

## Reinitialization

If you decide that in the process of neurons working something REALLY went wrong,
that follow the [reinitialization process](reinitialization.md) instruction.