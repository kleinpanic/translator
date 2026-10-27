#!/usr/bin/env bash

# Step 1: Determine if the program is installed system-wide or locally.
# A local checkout has ../src/translate.py next to this script; the
# system-wide copy lives in /usr/local/bin with the source elsewhere.
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [ -f "$DIR/../src/translate.py" ]; then
    echo "Local installation detected." >&2
    VENV_DIR="$DIR/../venv"
    SRC_FILE="$DIR/../src/translate.py"
else
    echo "System-wide installation detected." >&2
    VENV_DIR="/lib/python-venvs/translator-env"
    SRC_FILE="/usr/local/share/translator/src/translate.py"
fi

# Step 2: Double check that the virtual environments exist
if [ ! -d "$VENV_DIR" ]; then
    echo "Virtual environment not found at: $VENV_DIR" >&2
    echo "Please run the install script to set up the necessary environment." >&2
    exit 1
fi

# Print debugging information
echo "Using virtual environment at: $VENV_DIR" >&2
echo "Using source file at: $SRC_FILE" >&2

# Step 3: Use the virtual environment's python3 to run the main.py script
"$VENV_DIR/bin/python3" "$SRC_FILE" "$@"
status=$?

# Check for errors in running the script
if [ $status -ne 0 ]; then
    echo "An error occurred while running the translator" >&2
    exit $status
fi

