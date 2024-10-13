import subprocess
import os
import sys


# Function to run a shell command and capture its output
def run_command(command):
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    return result.stdout.strip()


# Function to check installed packages
def check_installed_packages():
    print("Checking installed Python packages...")
    installed_packages = run_command("pip list")
    print(installed_packages)
    return installed_packages


# Function to restart the validator processes if needed
def restart_process_if_needed():
    wallet_hotkey = os.getenv("WALLET_HOTKEY", "default")
    wallet_name = os.getenv("WALLET_NAME", "default")
    subtensor_network = os.getenv("SUBTENSOR_NETWORK", "finney")
    subtensor_chain_endpoint = os.getenv("SUBTENSOR_CHAIN_ENDPOINT", None)

    # Check if chain endpoint is specified, append the argument accordingly
    chain_endpoint_arg = (
        f"--subtensor.chain_endpoint {subtensor_chain_endpoint}"
        if subtensor_chain_endpoint
        else ""
    )

    # Define the PM2 process names
    proxy_process = f"validator_proxy_server_{wallet_hotkey}"
    server_process = f"validator_server_{wallet_hotkey}"

    # Restart the proxy process
    print(f"Restarting {proxy_process}...")
    restart_proxy_command = f"pm2 restart {proxy_process} --interpreter python3 -- --wallet.hotkey {wallet_hotkey} --wallet.name {wallet_name} --subtensor.network {subtensor_network} {chain_endpoint_arg}"
    run_command(restart_proxy_command)

    # Restart the validator process
    print(f"Restarting {server_process}...")
    restart_server_command = f"pm2 restart {server_process} --interpreter python3 -- --wallet.hotkey {wallet_hotkey} --wallet.name {wallet_name} --subtensor.network {subtensor_network} {chain_endpoint_arg}"
    run_command(restart_server_command)


def main():
    # # Activate the virtual environment if needed
    # venv_activate = os.getenv("VIRTUAL_ENV")
    # if venv_activate:
    #     activate_this = f"{venv_activate}/bin/activate_this.py"
    #     with open(activate_this) as f:
    #         exec(f.read(), {"__file__": activate_this})
    #
    # # Step 1: Check installed packages
    #

    print(check_installed_packages())


if __name__ == "__main__":
    main()
