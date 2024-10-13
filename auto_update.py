import os
import subprocess
import requests
import json

# Constants for file paths
LOCAL_CORE_VERSION_FILE = "tmp/local_core_version.txt"
PROXY_VERSION_URL = "https://localhost/version"

# Create temporary directory if it doesn't exist
if not os.path.exists("tmp"):
    os.makedirs("tmp")


def run_command(command):
    """Run a shell command and return the output."""
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error running command: {command}\n{result.stderr}")
    return result.stdout.strip()


def get_running_process_version():
    """Get the version of a PM2-managed process by its name."""
    # Use PM2 to fetch environment variables of the running process
    with open(LOCAL_CORE_VERSION_FILE, "r") as f:
        return f.read()


def get_local_core_version():
    """Get the version of the local core service."""
    print("Checking version in local code for the core service...")
    local_core_version = run_command(
        "python -c 'import neurons; print(neurons.__version__)'"
    )

    # Save to file
    with open(LOCAL_CORE_VERSION_FILE, "w") as f:
        f.write(local_core_version)

    return local_core_version


def get_proxy_version():
    """Get the version of the running and local proxy service."""

    print("Fetching version from the proxy service at https://localhost/version...")

    try:
        response = requests.get(PROXY_VERSION_URL, verify=False)
        running_proxy_version = response.json().get("version")
    except (requests.RequestException, json.JSONDecodeError) as e:
        print(f"Error fetching running proxy version: {e}")
        running_proxy_version = None

    print("Checking version in local code for the proxy service...")
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
    print(f"Restarting PM2 process: {process_name}...")
    run_command(f"pm2 restart {process_name}")


def update_git_repo():
    """Perform a git pull to update the repository if needed."""
    print("Fetching updates from GitHub...")
    git_pull_output = run_command("git pull")

    if "Already up to date." in git_pull_output:
        print("Local repository is up to date.")
        return False
    else:
        print("Repository updated from GitHub.")
        return True


def main():
    # Step 2: Update Git repository
    updated = update_git_repo()

    # Step 3: Fetch core service version from PM2
    running_core_version = get_running_process_version()
    local_core_version = get_local_core_version()

    # Step 4: Restart core service if necessary
    if updated or running_core_version != local_core_version:
        print(
            f"Core service version mismatch or update detected. Restarting core service..."
        )
        restart_pm2_process(f"validator_server_{os.getenv('WALLET_HOTKEY')}")

    # Step 5: Fetch proxy service versions
    running_proxy_version, local_proxy_version = get_proxy_version()

    # Step 6: Restart proxy service if necessary
    if running_proxy_version and running_proxy_version != local_proxy_version:
        print(f"Proxy service version mismatch detected. Restarting proxy service...")
        restart_pm2_process(f"validator_proxy_server_{os.getenv('WALLET_HOTKEY')}")
    else:
        print("Proxy service versions are the same. No restart required.")


if __name__ == "__main__":
    main()
