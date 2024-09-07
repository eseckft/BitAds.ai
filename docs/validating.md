# Validating

## Overview

This document provides detailed instructions for deploying, launching, reinitializing, and performing subsequent
important steps for the validator project. The steps include setting up the environment, running the validator scripts,
and using the auto-update feature. **Important: Ensure that port 443 is open and available, as it is required for secure
HTTPS communication with the validator. All validator commands should be run from the `sudo su -` environment to avoid
permission issues.**

## Table of Contents

1. [Deployment](#deployment)
    - [Creating a Virtual Environment](#creating-a-virtual-environment)
    - [Country Detection](#country-detection)
    - [Git Clone the repositroy](#git-clone-the-repository)
    - [Create account on BitAds.ai (Mandatory)](#create-account-on-bitadsai-mandatory)
    - [Installing Dependencies](#installing-dependencies) 
2. [Launch](#launch)
    - [Running the Validator with Auto-Update](#running-the-validator-with-auto-update)
    - [Example Command](#example-command)
3. [Subsequent Important Steps](#subsequent-important-steps)
4. [Reinitialization](#reinitialization)

## Deployment

### Creating a Virtual Environment

Creating a virtual environment is an optional but recommended step to manage dependencies and isolate the project
environment. The required Python version is 3.11+.

**Note:** Ensure that port 443 is open and available. This port is used for secure communication (HTTPS) between your
validator and external systems, such as the BitAds.ai platform. Without this, the validator won't be able to communicate
securely.

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

**Important:** After creating the environment, **all subsequent commands should be executed as the root user** to avoid
permission issues. This can be done by switching to the `sudo su -` environment before proceeding:

```bash
sudo su -
```

### Country Detection

Download the Geo2Lite database, which is required for the project to detect and store the country information of IP
addresses:

```bash
wget https://git.io/GeoLite2-Country.mmdb
```

### Git Clone the Repository

```bash
git clone https://github.com/eseckft/BitAds.ai.git
cd BitAds.ai
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

4. **Update/install sqlite3**

   ```bash
   apt update
   apt install sqlite3
   ```

### Create account on BitAds.ai (Mandatory)

Validator registration is required. This allows the server to ping, informing us of your activity so we can include it in the DNS records, ensuring the participant is accessible via x.bitads.ai or v.bitads.ai. <br><br>
Without an account, Validators won't be able to set weights on the subnet. Having an account gives Validators easy access to miner and campaign statistics, as well as the API key needed to build their own application on the BitAds subnet. <br><br>
Validators will be manually approved after we receive written confirmation on Discord regarding their registration.<br><br>
For any inquiries regarding script usage or registration, please refer to the official documentation on BitAds.ai or contact our support team.<br>
You can register here: [BitAds.ai](https://bitads.ai/register)


## Launch

### Generating a Self-Signed SSL Certificate

To secure the communication for your validator server, you may need to generate a self-signed SSL certificate. This can
be done using OpenSSL. Follow the steps below to create the certificate and key files:

```bash
openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout key.pem \
    -out cert.pem \
    -subj "/C=US/ST=State/L=City/O=Bitads/CN=localhost"
```

**Note:** Port 443 must be open and available on your system for secure communication over HTTPS.

### Example Command

To run the validator with auto-update, use the following command:

```bash
pm2 start run_validator_auto_update.py --interpreter python3 -- --subtensor.network local --wallet.name <name> --wallet.hotkey <name>
```

- Replace `<name>` with your wallet name and hotkey.
- This command uses `pm2` to manage the process, ensuring it stays running and is easily restartable.

**Important:** Ensure you are running this command in the `sudo su -` environment to avoid permission issues.

---

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

**Reminder:** Always ensure port 443 is open for secure communication, and make sure you're in the `sudo su -`
environment when running these commands.

---

## Reinitialization

If you decide that in the process of neurons working something REALLY went wrong, follow
the [reinitialization process](reinitialization.md) instruction.
