#!/usr/bin/env bash

# Function to check for required dependencies
check_dependencies() {
    echo "Checking for required dependencies..."

    # Check if Python is installed
    if ! command -v python3 &> /dev/null; then
        echo "Python3 is not installed. Please install it and try again."
        exit 1
    fi

    # Check if venv is installed
    if ! python3 -m venv --help &> /dev/null; then
        echo "Python venv is not installed. Please install it and try again."
        exit 1
    fi

    echo "All dependencies are satisfied."
}

# Function to choose installation type
choose_install_type() {
    echo "Do you want to install the program locally or system-wide?"
    echo "0) Cancel"
    echo "1) Locally (current user)"
    echo "2) System-wide (requires sudo)"
    read -p "Choose an option [0/1/2]: " install_option

    # Check if the input is valid
    if [[ -z "$install_option" || ! "$install_option" =~ ^[012]$ ]]; then
        echo "Invalid option. Exiting."
        exit 1
    fi

    # If the user chooses to cancel
    if [ "$install_option" -eq 0 ]; then
        echo "Installation canceled."
        exit 0
    fi

    return $install_option
}

# Function for local installation
local_install() {
    echo "Starting local installation..."
    VENV_DIR="$DIR/../venv"
    SRC_FILE="$DIR/../src/translate.py"

    # Check if the virtual environment exists, if not, create it
    if [ ! -d "$VENV_DIR" ]; then
        echo "Creating virtual environment..."
        python3 -m venv "$VENV_DIR"
    fi

    # Install the required packages
    echo "Installing dependencies..."
    "$VENV_DIR/bin/pip" install -r "$DIR/requirements.txt"

    # Make the wrapper script executable
    chmod +x "$DIR/translate.sh"

    echo "Local install complete. Manually run the startup script using ./translate.sh"
}

# Function for system-wide installation
system_wide_install() {
    echo "Starting system-wide installation..."
    VENV_DIR="/lib/python-venvs/translator-env"
    SRC_DIR="/usr/local/share/translator/src"

    # Create a directory for system-wide Python virtual environments if it doesn't exist
    if [ ! -d "/lib/python-venvs" ]; then
        sudo mkdir -p /lib/python-venvs
        sudo chmod 755 /lib/python-venvs
    fi

    # Check if the virtual environment exists, if not, create it
    if [ ! -d "$VENV_DIR" ]; then
        echo "Creating system-wide virtual environment..."
        sudo python3 -m venv "$VENV_DIR"
    fi

    # Install the required packages
    echo "Installing dependencies system-wide..."
    sudo "$VENV_DIR/bin/pip" install -r "$DIR/requirements.txt"

    # Create the necessary directories and copy the source code
    sudo mkdir -p "$SRC_DIR"
    sudo cp "$DIR/../src/"* "$SRC_DIR/"

    # Create the translate script with updated paths
    sudo cp "$DIR/translate.sh" "/usr/local/bin/translate"
    sudo chmod +x "/usr/local/bin/translate"

    echo "Global install complete. Run 'translate' from /usr/local/bin or in the shell."
}

# Main installation logic
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
check_dependencies
choose_install_type
install_option=$?

if [ "$install_option" -eq 1 ]; then
    local_install
elif [ "$install_option" -eq 2 ]; then
    system_wide_install
fi

