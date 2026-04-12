#!/usr/bin/env bash

set -euo pipefail

REPO_URL="https://github.com/Vishvesh1542/dotfiles.git"
DEST_DIR="$HOME/.files"

for cmd in git curl sudo; do
    if ! command -v "$cmd" &> /dev/null; then
        echo "Error: $cmd is not installed. Please install it first."
        exit 1
    fi
done

if [ ! -d "$DEST_DIR/.git" ]; then
    echo "Cloning repository to $DEST_DIR..."
    mkdir -p "$DEST_DIR"
    cd "$DEST_DIR"
    git clone "$REPO_URL" .
else
    echo "Directory exists. Pulling latest changes..."
    cd "$DEST_DIR" && git pull origin main
fi

cd "$DEST_DIR"

if ! command -v just &> /dev/null; then
    echo "Installing just..."
    sudo pacman -S --noconfirm --needed just
fi

echo "--- Starting installation ---"
if [ -f "justfile" ]; then
    just setup-computer
else
    echo "Error: justfile not found in $DEST_DIR"
    exit 1
fi

echo "Installation complete."
