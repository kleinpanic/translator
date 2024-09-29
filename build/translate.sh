#!/usr/bin/env bash

# Step 1: Determine if the program is installed system-wide or locally
if [ -f "/usr/local/bin/translate" ]; then
    echo "System-wide installation detected."
    VENV_DIR="/lib/python-venvs/translator-env"
    SRC_FILE="/usr/local/share/translator/src/translate.py"
else
    echo "Local installation detected."
    # Determine the directory the script is being run from
    DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    VENV_DIR="$DIR/../venv"
    SRC_FILE="$DIR/../translate.py"
fi

# Step 2: Double check that the virtual environments exist
if [ ! -d "$VENV_DIR" ]; then
    echo "Virtual environment not found at: $VENV_DIR"
    echo "Please run the install script to set up the necessary environment."
    exit 1
fi

# Print debugging information
echo "Using virtual environment at: $VENV_DIR"
echo "Using source file at: $SRC_FILE"

# Step 3: Use the virtual environment's python3 to run the main.py script
"$VENV_DIR/bin/python3" "$SRC_FILE" "$@"

# Check for errors in running the script
if [ $? -ne 0 ]; then
    echo "An error occurred while running the translator"
    exit 1
fi

