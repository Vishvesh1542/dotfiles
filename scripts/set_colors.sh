#!/bin/bash
# @vicinae.schemaVersion 1
# @vicinae.title Accent Color
# @vicinae.mode silent
# @vicinae.argument1 { "type": "text", "placeholder": "color" }

case "$1" in
    blue)    ACCENT="blue";    HEX="#3584e4" ;;
    teal)    ACCENT="teal";    HEX="#2190a4 " ;;
    green)   ACCENT="green";   HEX="#2ec27e" ;;
    yellow)  ACCENT="yellow";  HEX="#f6d32d" ;;
    orange)  ACCENT="orange";  HEX="#ff7800" ;;
    red)     ACCENT="red";     HEX="#e01b24" ;;
    pink)    ACCENT="pink";    HEX="#d56199" ;;
    purple)  ACCENT="purple";  HEX="#9141ac" ;;
    slate)   ACCENT="slate";   HEX="#637683" ;;
    brown)   ACCENT="brown";   HEX="#986a44"  ;;
    *)
        echo "blue | teal | green | yellow | orange | red | pink | purple | slate | brown"
        exit 1
        ;;
esac

# 1. Update GNOME settings
/bin/gsettings set org.gnome.desktop.interface accent-color "$ACCENT"
/bin/gsettings set org.gnome.desktop.interface icon-theme "Adwaita-$ACCENT"

# Update the config for niri
/bin/awk -v color="$HEX" -i inplace '/active-color/ {
    gsub(/#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})/, color);
} { print }' "$HOME/.config/niri/colors.kdl"

niri msg action do-screen-transition --delay-ms 50
echo "Set Accent color to $ACCENT and reloaded stuff"
