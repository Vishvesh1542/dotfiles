#!/bin/bash

# Get the current setting
CURRENT_SCHEME=$(gsettings get org.gnome.desktop.interface color-scheme)

if [ "$CURRENT_SCHEME" = "'prefer-dark'" ]; then
    # Switch to light mode
    gsettings set org.gnome.desktop.interface color-scheme "default"
else
    # Switch to dark mode
    gsettings set org.gnome.desktop.interface color-scheme "prefer-dark"
fi

# Run your Niri transition
niri msg action do-screen-transition --delay-ms 0
