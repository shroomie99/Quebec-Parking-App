import os
import subprocess
import sys

def install_packages():
    # Check if Python is installed
    try:
        python_version = subprocess.check_output(["python", "--version"])
        print(f"Python found: {python_version.decode('utf-8').strip()}")
    except FileNotFoundError:
        print("Python is not installed. Please install Python and try again.")
        sys.exit(1)

    # Check if pip is installed
    try:
        pip_version = subprocess.check_output(["pip", "--version"])
        print(f"pip found: {pip_version.decode('utf-8').strip()}")
    except FileNotFoundError:
        print("pip is not installed. Please install pip and try again.")
        sys.exit(1)

    # Install packages from requirements.txt
    if os.path.exists("requirements.txt"):
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
    else:
        print("requirements.txt file is missing. Cannot install dependencies.")
        sys.exit(1)

    print("All required packages are installed.")

if __name__ == "__main__":
    install_packages()
