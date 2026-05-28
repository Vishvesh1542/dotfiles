#!/bin/bash

# Define paths
PROFILE_PATH="/sys/firmware/acpi/platform_profile"
CHOICES_PATH="/sys/firmware/acpi/platform_profile_choices"

# Check if ACPI platform profiles are supported on this hardware
if [ ! -f "$PROFILE_PATH" ]; then
    echo "Error: ACPI platform profiles are not supported on this system."
    exit 1
fi

# Function to show current status
show_status() {
    echo "====================================="
    echo "  Current Profile: $(cat $PROFILE_PATH)"
    echo "  Available Options: $(cat $CHOICES_PATH)"
    echo "====================================="
}

# If no arguments are passed, show status and menu
if [ -z "$1" ]; then
    show_status
    echo "Choose a profile to set:"
    
    # Read choices into an array
    choices=($(cat "$CHOICES_PATH"))
    
    # Loop through choices and create a menu
    select opt in "${choices[@]}" "Quit"; do
        if [ "$opt" = "Quit" ]; then
            echo "Exiting."
            exit 0
        elif [ -n "$opt" ]; then
            echo "Setting profile to: $opt"
            echo "$opt" | sudo tee "$PROFILE_PATH" > /dev/null
            break
        else
            echo "Invalid selection."
        fi
    done
else
    # If an argument is passed (e.g., ./script.sh performance)
    TARGET_PROFILE="$1"
    AVAILABLE_CHOICES=$(cat "$CHOICES_PATH")
    
    # Validate if the passed argument is valid for this hardware
    if [[ " $AVAILABLE_CHOICES " =~ " $TARGET_PROFILE " ]]; then
        echo "Setting profile to: $TARGET_PROFILE"
        echo "$TARGET_PROFILE" | sudo tee "$PROFILE_PATH" > /dev/null
    else
        echo "Error: '$TARGET_PROFILE' is not a valid profile for this machine."
        echo "Available options are: $AVAILABLE_CHOICES"
        exit 1
    fi
fi
