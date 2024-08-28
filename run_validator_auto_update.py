import importlib
import os
import subprocess
import sys
import time

import requests

from common.validator.environ import Environ


def should_update_local(local_commit, remote_commit):
    return local_commit != remote_commit


args = " ".join(sys.argv[1:])

os.system(f"./start_validators.sh {args} --restart-proxy")
time.sleep(10)

REMOTE = os.environ.get("REMOTE", "origin")


def auto_update_script(remote: str = REMOTE):
    current_branch = subprocess.getoutput("git rev-parse --abbrev-ref HEAD")
    local_commit = subprocess.getoutput("git rev-parse HEAD")
    os.system(f"git fetch {remote}")
    remote_commit = subprocess.getoutput(f"git rev-parse {remote}/{current_branch}")

    if should_update_local(local_commit, remote_commit):
        print("Local repo is not up-to-date. Updating...")
        reset_cmd = "git reset --hard " + remote_commit
        process = subprocess.Popen(reset_cmd.split(), stdout=subprocess.PIPE)
        output, error = process.communicate()

        if error:
            print("Error in updating:", error)
        else:
            print(
                "Updated local repo to latest version: {}",
                format(remote_commit),
            )

            print("Running the autoupdate steps...")
            # Trigger shell script. Make sure this file path starts from root
            should_restart_proxy = auto_update_proxy()
            os.system(
                f"./start_validators.sh {args}"
                + (" --restart-proxy" if should_restart_proxy else "")
            )
            time.sleep(20)

            print("Finished running the autoupdate steps! Ready to go 😎")

    else:
        print("Repo is up-to-date.")


def auto_update_proxy() -> bool:
    try:
        response = requests.get(f"https://localhost/version", verify=False)
        print(f"Version response: {response.text}")
    except requests.ConnectionError:
        print("Connection error while fetching proxy version")
        return False
    else:
        runtime_app_version = response.json().get("version")

        app_module = importlib.reload(importlib.import_module("proxies.validator"))
        app = getattr(app_module, "app")
        local_app_version = getattr(app, "version")
        print(
            f"Local app version: {local_app_version}.",
            f"Runtime app version: {runtime_app_version}",
        )
        return local_app_version != runtime_app_version


def run_auto_updater():
    while True:
        auto_update_script()
        time.sleep(60)


if __name__ == "__main__":
    run_auto_updater()
