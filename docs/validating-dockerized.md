# Validating

## Overview

This document provides detailed instructions for deploying, launching, reinitializing, and performing subsequent important steps for the validating project. The steps include setting up the environment, running the validator scripts, and using the auto-update feature.

> **Note:** You can choose to use Docker instead of the default deployment. Docker simplifies the process by eliminating the need to manually manage dependencies and environment configurations. See the [Docker Installation](#install-docker-and-docker-compose) and [Running the validator with Docker Compose](#running-the-validator-with-docker-compose) sections for details.

## Table of Contents

1. [Deployment](#deployment)
    - [Creating a Virtual Environment](#creating-a-virtual-environment)
    - [Git Clone the Repository](#clone-the-repository)
    - [Installing Dependencies](#installing-dependencies)
    - [Configure the .env File](#configure-the-env-file)
    - [Install Docker and Docker Compose](#install-docker-and-docker-compose)
    - [Installing Bittensor or Bittensor-CLI](#installing-bittensor-or-bittensor-cli)
    - [Create Account on BitAds.ai (Mandatory)](#create-account-on-bitadsai-mandatory)
2. [Launch](#launch)
    - [Running the validator with Docker Compose](#running-the-validator-with-docker-compose)
    - [Auto-Update with Cron](#auto-update-with-cron)
    - [Auto-Update with PM2](#auto-update-with-pm2)
    - [Example Command](#example-command)
3. [Subsequent Important Steps](#subsequent-important-steps)
4. [Reinitialization](#reinitialization)

---

## Deployment

### Creating a Virtual Environment

Creating a virtual environment is an optional but recommended step to manage dependencies and isolate the project environment. The required Python version is 3.11+.

1. **Install Python 3.11+**:  
   Ensure that Python 3.11+ is installed on your system. You can download it from the [official Python website](https://www.python.org/downloads/).

2. **Clone the Repository**:

   ```bash
   git clone https://github.com/eseckft/BitAds.ai.git
   cd BitAds.ai
   ```

3. **Create a Virtual Environment**:

   ```bash
   python3 -m venv venv
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

### Installing Dependencies

1. **Upgrade `pip`**:

   ```bash
   python3 -m pip install --upgrade pip
   ```

2. **Install Required Packages**:

   If you are not using Docker, all dependencies listed in the `requirements.txt` file are required for the default setup. Install them using the following command:

   ```bash
   pip install bittensor
   ```

   > **Note:** Only the `bittensor` or `bittensor-cli` package is needed to manage or create new wallets.

---

### Configure the `.env` File

The `.env` file is used to store environment-specific configuration variables for the validator. Follow these steps to configure the `.env` file:

1. **Open the `.env` file**:
   
   To edit the `.env` file, use any text editor of your choice. If you do not have a preferred editor, you can install `nano`, a simple terminal-based text editor:

   ```bash
   sudo apt install nano
   ```

2. **Edit the `.env` file**:

   Open the `.env` file using `nano` or any other editor:

   ```bash
   nano .env
   ```

   If you're using a different editor like `vim`, you can replace `nano` with `vim`:

   ```bash
   vim .env
   ```

3. **Set Environment Variables**:

   Update the `.env` file with the necessary configuration values. The example values to modify include:

   ```bash
   # Subtensor Configuration
       # Subtensor Network
   SUBTENSOR_NETWORK=finney
       # Subtensor Chain Endpoint
   SUBTENSOR_CHAIN_ENDPOINT=wss://entrypoint-finney.opentensor.ai:443
   
   # Wallet Configuration
       # Your wallet name goes here
   WALLET_NAME=default
       # Your wallet hotkey goes here
   WALLET_HOTKEY=default
   
   # Neuron Type
       # Specify the type of neuron (e.g., validator, proxy)
   NEURON_TYPE=validator
   
   # Axon Port Configuration
   AXON_PORT=8081
   ```

4. **Save and Exit**:

   - If using `nano`, save changes by pressing `CTRL + O` and exit by pressing `CTRL + X`.
   - If using `vim`, press `ESC`, then type `:wq` to save and quit.

---

### Install Docker and Docker Compose

1. **Install Docker**:  
   Follow the installation guide on the [official Docker website](https://docs.docker.com/get-docker/) to install Docker.

2. **Install Docker Compose**:  
   Most Docker installations include Docker Compose, but you can confirm by running:

   ```bash
   docker compose version
   ```

   If it's not installed, you can follow the instructions [here](https://docs.docker.com/compose/install/).

> **Note:** Although Docker simplifies most of the deployment, you still need to install either the `bittensor` or `bittensor-cli` package (with or without a virtual environment) to manage or create new wallets. Follow the [Installing Bittensor or Bittensor-CLI](#installing-bittensor-or-bittensor-cli) section for more details.

---

### Installing Bittensor or Bittensor-CLI

To manage wallets for mining, you need to install either the `bittensor` SDK or the `bittensor-cli`. These tools allow you to create or import wallets.

1. **Bittensor (Full SDK)**:
   Install the full Bittensor SDK using `pip`:

   ```bash
   pip install bittensor
   ```

2. **Bittensor-CLI (Command-line Interface)**:
   If you prefer a lightweight command-line interface for managing wallets, you can install `bittensor-cli`:

   ```bash
   pip install bittensor-cli
   ```

Both tools will allow you to create, import, or manage your wallets before starting the mining process.

---

### Create Account on BitAds.ai (Mandatory)

Validator registration is required. This allows the server to ping, informing us of your activity so we can include it in the DNS records, ensuring the participant is accessible via x.bitads.ai or v.bitads.ai. <br><br>
Without an account, Validators won't be able to set weights on the subnet. Having an account gives Validators easy access to miner and campaign statistics, as well as the API key needed to build their own application on the BitAds subnet. <br><br>
Validators will be manually approved after we receive written confirmation on Discord regarding their registration.<br><br>
For any inquiries regarding script usage or registration, please refer to the official documentation on BitAds.ai or contact our support team.<br>
You can register here: [BitAds.ai](https://bitads.ai/register)

---

## Launch

### Running the validator with Docker Compose

To run the validator using Docker Compose, follow these steps:

1. **Build and Start the Containers**:

   ```bash
   docker compose up --build
   ```

   This command builds the Docker image (if necessary) and runs the containers for the validator services.

2. **Stop the Containers**:

   ```bash
   docker compose down
   ```

This will stop and remove the containers while preserving data.

---

### Auto-Update with Cron

To set up auto-updating via cron, add the following cron job to periodically check for updates and restart services if needed:

1. **Add the Cron Job**:

   Run this command to set up a cron job that runs every minute:

   ```bash
   (echo "* * * * * /bin/bash $(pwd)/update_and_compare.sh >> $(pwd)/cron.log 2>&1"; crontab -l) | crontab -
   ```

2. **Monitor the Cron Logs**:

   The logs for this cron job will be stored in `cron.log` in the project directory. You can view them with:

   ```bash
   tail -f cron.log
   ```

---

### Auto-Update with PM2

**Note:** PM2 is commonly used to manage Node.js processes, but it can also be used to manage Python scripts or other long-running commands.

1. **Install PM2**:

   Install PM2 globally using npm:

   ```bash
   npm install -g pm2
   ```

2. **Configure PM2 for Auto-Update**:

   Use PM2 to schedule the execution of the `update_and_compare.sh` script, which will automatically check for updates and rebuild your Docker containers as needed. The following command sets up the auto-update task to run every minute using PM2's built-in cron scheduling:

   ```bash
   pm2 start update_and_compare.sh --cron="* * * * *" --no-autorestart
   ```

3. **Monitor PM2 Tasks**:

   Use the following command to view the status of your PM2-managed tasks:

   ```bash
   pm2 list
   ```

4. **View Logs**:

   You can view the logs generated by your auto-update task by using:

   ```bash
   pm2 logs update_and_compare.sh
   ```

---

### Example Command

To run the validator with auto-update using Docker Compose, use the following command:

```bash
docker compose up --build
```

---

## Subsequent Important Steps

1. **Monitor the Validator**:  
   Use `docker` commands to monitor the status of your validator containers. For example:

   ```bash
   docker ps
   ```

2. **Handling Updates**:  
   The `update_and_compare.sh` script automatically handles updates. Ensure that it is running correctly via cron or another process manager like PM2 to keep your validator up-to-date.

3. **Restarting Containers**:  
   If necessary, you can manually restart the validator or proxy containers using Docker:

   ```bash
   docker compose restart core
   docker compose restart proxy
   ```

4. **Logging and Debugging**:  
   Check the logs for any issues or errors:

   ```bash
   docker compose logs core
   docker compose logs proxy
   ```

---

## Reinitialization

If you decide that in the process of neurons working something really went wrong, follow the [reinitialization process](reinitialization.md) instruction.

---

### Notes:

- **Docker Installation**: While Docker simplifies the deployment process, remember that you still need the `bittensor` or `bittensor-cli` package to manage wallets. This can be done either with or without a virtual environment.
