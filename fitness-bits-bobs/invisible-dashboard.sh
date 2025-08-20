#!/bin/bash

# Wait just 1 second
sleep 1

# Set display
export DISPLAY=:0

# Immediately kill all desktop components
pkill lxpanel &
pkill pcmanfm &
pkill lxde-pi-shutdown-helper &

# Set black background immediately
xsetroot -solid black

# Hide cursor
unclutter -idle 0.1 &

# Disable screen blanking
xset s off
xset -dpms
xset s noblank

# Wait minimal time for PM2
sleep 8

# Launch dashboard - this will cover everything
chromium-browser \
  --kiosk \
  --no-sandbox \
  --disable-infobars \
  --noerrdialogs \
  --start-fullscreen \
  --disable-context-menu \
  --touch-events=enabled \
  --window-position=0,0 \
  --autoplay-policy=no-user-gesture-required \
  http://localhost:3000 &

# Wait a moment then kill any remaining desktop elements
sleep 3
pkill lxpanel
pkill pcmanfm
