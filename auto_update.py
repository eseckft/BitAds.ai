import os
import subprocess
import requests
import json
import logging
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Constants
LOCAL_CORE_VERSION_FILE = "tmp/local_core_version.txt"
PROXY_VERSION_URL = "https://localhost/version"
TMP_DIR = "tmp"

# Ensure temporary directory exists
os.makedirs(TMP_DIR, exist_ok=True)

# Configure logging
logging.basicConfig(
    level=logging.INFO,  # Set logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    format="%(asctime)s - %(levelname)s - %(message)s",  # Format of log messages
)


def run_command(command):
    """Run a shell command and return the output."""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode != 0:
            logging.error(f"Command failed: {command}\n{result.stderr}")
        return result.stdout.strip()
    except Exception as e:
        logging.error(f"Error running command: {e}")
        return ""


def read_file(file_path):
    """Read and return the content of a file, or None if an error occurs."""
    if not os.path.exists(file_path):
        logging.warning(f"File not found: {file_path}")
        return None
    try:
        with open(file_path, "r") as file:
            return file.read().strip()
    except IOError as e:
        logging.error(f"Error reading file {file_path}: {e}")
    return None


def write_file(file_path, content):
    """Write content to a file."""
    try:
        with open(file_path, "w") as file:
            file.write(content)
    except IOError as e:
        logging.error(f"Error writing to file {file_path}: {e}")


def get_local_core_version():
    """Fetch and save the local core service version."""
    logging.info("Checking version in local code for the core service...")
    local_core_version = run_command(
        "python -c 'import neurons; print(neurons.__version__)'"
    )
    if local_core_version:
        write_file(LOCAL_CORE_VERSION_FILE, local_core_version)
    return local_core_version


def get_proxy_version():
    """Fetch the version of the running and local proxy service."""
    logging.info(
        "Fetching version from the proxy service at https://localhost/version..."
    )

    try:
        response = requests.get(PROXY_VERSION_URL, verify=False)
        running_proxy_version = response.json().get("version")
    except (requests.RequestException, json.JSONDecodeError, Exception) as e:
        logging.error(f"Error fetching running proxy version: {e}")
        running_proxy_version = None

    logging.info("Checking version in local code for the proxy service...")
    local_proxy_version = run_command(
        """python -c '
import proxies
import os
neuron_type = os.getenv("NEURON_TYPE")
print(getattr(proxies, f"__{neuron_type}_version__"))
'"""
    )
    return running_proxy_version, local_proxy_version


def restart_pm2_process(process_name):
    """Restart a PM2-managed process."""
    logging.info(f"Restarting PM2 process: {process_name}...")
    run_command(f"pm2 restart {process_name}")


def update_git_repo():
    """Perform a git pull to update the repository if needed."""
    logging.info("Fetching updates from GitHub...")
    git_pull_output = run_command("git pull")

    if "Already up to date." in git_pull_output:
        logging.info("Local repository is up to date.")
        return False
    else:
        logging.info("Repository updated from GitHub.")
        return True


def build_project(wallet_name, wallet_hotkey, neuron_type):
    """Build the project using the provided wallet and neuron parameters."""
    logging.info("Building project with updated parameters...")
    run_command(
        f"./build_project.sh --wallet.name {wallet_name} "
        f"--wallet.hotkey {wallet_hotkey} --neuron.type {neuron_type}"
    )


def main():
    # Step 1: Update Git repository
    updated = update_git_repo()

    # Only proceed with version checks and builds if an update was received

    # Step 2: Load environment variables
    wallet_name = os.getenv("WALLET_NAME")
    wallet_hotkey = os.getenv("WALLET_HOTKEY")
    neuron_type = os.getenv("NEURON_TYPE")

    # Step 3: Fetch core service version
    running_core_version = read_file(LOCAL_CORE_VERSION_FILE)
    if running_core_version is None:
        logging.info(
            "No previous core service version found. This seems to be the first run."
        )

    local_core_version = get_local_core_version()

    # Step 5: Restart core service if versions differ
    if running_core_version != local_core_version:
        build_project(wallet_name, wallet_hotkey, neuron_type)

        logging.info(
            "Core service version mismatch or update detected. Restarting core service..."
        )
        restart_pm2_process(f"{neuron_type}_server_{wallet_hotkey}")

    # Step 6: Fetch proxy service versions
    running_proxy_version, local_proxy_version = get_proxy_version()

    # Step 7: Restart proxy service if versions differ
    if running_proxy_version != local_proxy_version:
        logging.info(
            "Proxy service version mismatch detected. Restarting proxy service..."
        )
        restart_pm2_process(f"{neuron_type}_proxy_server_{wallet_hotkey}")
    else:
        logging.info("Proxy service versions are the same. No restart required.")


if __name__ == "__main__":
    main()
