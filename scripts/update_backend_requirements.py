import os
import subprocess


def check_command_exists(command):
    try:
        subprocess.run([command, "--version"], subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except FileExistsError:
        return False


def main():

    if not check_command_exists("git"):
        print("Error: git is not isntalled or is not in the system PATH")
        exit(1)

    script_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(script_dir)

    venv_pip = os.path.join(parent_dir, "analyticq-backend", "venv", "bin", "pip")
    if os.name == "nt":  # Handle Win case
        venv_pip = os.path.join(parent_dir, "analyticq-backend", "venv", "Scripts", "pip.exe")

    if not os.path.exists(venv_pip):
        print(f"Error: pip command not found at {venv_pip}. Are you sure your venv is and running?")
        exit(1)

    with open("requirements.txt", "w") as f:
        subprocess.run([venv_pip, "freeze"], stdout=f)

    result = subprocess.run(["git", "diff", "--exit-code", "requirements.txt"])
    if result.returncode != 0:
        print("requirements.txt is outdated. Please update it before committing.")
        exit(1)


if __name__ == "__main__":
    main()
