#!/usr/bin/env bash

set -e

REPO_URL="https://github.com/Vishvesh1542/dotfiles.git"
DEST_DIR="$HOME/.files"

echo "--- Preparing installation ---"

echo "Cloning repository to $DEST_DIR..."
git clone "$REPO_URL" "$DEST_DIR" .

cd "$DEST_DIR"

if ! command -v just &> /dev/null; then
    sudo pacman -S just
    export PATH="$HOME/.local/bin:$PATH"
fi

just setup-computer
