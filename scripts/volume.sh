#!/bin/bash

# Change this value to adjust the step size
STEP="5%"

case $1 in
    up)
        # Unmutes and increases volume, capped at 1.0 (100%)
        wpctl set-mute @DEFAULT_AUDIO_SINK@ 0
        wpctl set-volume -l 1.0 @DEFAULT_AUDIO_SINK@ $STEP+
        # Play the feedback sound
        canberra-gtk-play -i audio-volume-change -d "change-volume"
        ;;
    down)
        # Decreases volume
        wpctl set-volume @DEFAULT_AUDIO_SINK@ $STEP-
        # Play the feedback sound
        canberra-gtk-play -i audio-volume-change -d "change-volume"
        ;;
    mute)
        # Toggles mute status
        wpctl set-mute @DEFAULT_AUDIO_SINK@ toggle
        ;;
    micmute)
        wpctl set-mute @DEFAULT_AUDIO_SOURCE@ toggle
        ;;
    *)
        # Catch-all for incorrect arguments
        echo "Usage: $0 {up|down|mute|micmute}"
        exit 1
        ;;
esac
