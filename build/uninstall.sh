#!/usr/bin/env bash

# Function to confirm uninstallation
confirm_uninstall() {
    echo "Are you sure you want to uninstall the translate program?"
    echo "This will remove the virtual environment and all installed files."
    read -r -p "Type 'yes' to proceed: " confirmation

    if [ "$confirmation" != "yes" ]; then
        echo "Uninstallation canceled."
        exit 0
    fi
}

# Function for local uninstallation
local_uninstall() {
    echo "Starting local uninstallation..."

    # Remove the virtual environment directory
    if [ -d "$VENV_DIR" ]; then
        echo "Removing virtual environment..."
        rm -rf "$VENV_DIR"
    fi

    # Optionally remove the src/translator.py file if needed (commented out by default)
    # Uncomment the following lines if you want to remove the source code as well
    # echo "Removing source code..."
    # rm -rf "$DIR/../src/translator.py"

    echo "Local uninstallation complete."
}

# Function for system-wide uninstallation
system_wide_uninstall() {
    echo "Starting system-wide uninstallation..."

    # Remove the system-wide virtual environment
    if [ -d "$SYS_VENV_DIR" ]; then
        echo "Removing system-wide virtual environment..."
        sudo rm -rf "$SYS_VENV_DIR"
    fi

    # Remove the source code directory
    if [ -d "$SRC_DIR" ]; then
        echo "Removing source code..."
        sudo rm -rf "$SRC_DIR"
    fi

    # Remove the translate executable from /usr/local/bin
    if [ -f "$BIN_FILE" ]; then
        echo "Removing translate executable..."
        sudo rm "$BIN_FILE"
    fi

    echo "System-wide uninstallation complete."
}

# Main uninstallation logic
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
VENV_DIR="$DIR/../venv"
# Overridable so the script can be exercised in tests without touching /.
SYS_VENV_DIR="${TRANSLATOR_SYS_VENV_DIR:-/lib/python-venvs/translator-env}"
SRC_DIR="${TRANSLATOR_SRC_DIR:-/usr/local/share/translator/src}"
BIN_FILE="${TRANSLATOR_BIN_FILE:-/usr/local/bin/translate}"

# Confirm uninstallation
confirm_uninstall

# Determine installation type (local or system-wide) based on the presence of /usr/local/bin/translate
if [ -f "$BIN_FILE" ]; then
    system_wide_uninstall
else
    local_uninstall
fi

