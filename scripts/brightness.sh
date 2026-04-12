#!/bin/bash

STEP="5%"

case $1 in
    up)
        brightnessctl set $STEP+
        ;;
    down)
        brightnessctl set $STEP-
        ;;
    *)
        echo "Usage: $0 {up|down}"
        exit 1
        ;;
esac
