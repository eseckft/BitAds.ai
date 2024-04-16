import os
import subprocess
import time


def get_remote_commit_if_needed():
    local_commit = get_local_commit()
    remote_commit = get_remote_commit()
    return remote_commit if local_commit != remote_commit else None


def get_local_commit():
    local_commit = subprocess.getoutput("git rev-parse HEAD")
    return local_commit


def get_remote_commit():
    current_branch = subprocess.getoutput("git rev-parse --abbrev-ref HEAD")
    remote_commit = subprocess.getoutput(f"git rev-parse github/{current_branch}")
    return remote_commit


os.system("./start_miners.sh")
time.sleep(10)


def run_auto_updater():
    while True:
        os.system("git fetch github")

        if remote_commit := get_remote_commit_if_needed():
            print("Local repo is not up-to-date. Updating...")
            reset_cmd = "git reset --hard " + remote_commit
            process = subprocess.Popen(reset_cmd.split(), stdout=subprocess.PIPE)
            output, error = process.communicate()

            if error:
                print("Error in updating:", error)
            else:
                print("Updated local repo to latest version: {}", format(remote_commit))

                print("Running the autoupdate steps...")
                # Trigger shell script. Make sure this file path starts from root
                # os.system("./autoupdate_miner_steps.sh")
                time.sleep(20)

                print("Finished running the autoupdate steps! Ready to go 😎")

        else:
            print("Repo is up-to-date.")

        time.sleep(60)


if __name__ == "__main__":
    run_auto_updater()
