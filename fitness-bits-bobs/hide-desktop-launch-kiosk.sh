#!/bin/bash

# Immediately hide desktop elements
export DISPLAY=:0
sleep 2

# Kill desktop components immediately
pkill lxpanel
pkill pcmanfm
pkill lxde-pi-shutdown-helper

# Set black background immediately
xsetroot -solid black

# Hide cursor
unclutter -idle 0.1 &

# Disable screen blanking
xset s off
xset -dpms
xset s noblank

# Wait minimal time for PM2
sleep 10

# Launch dashboard
chromium-browser \
  --kiosk \
  --no-sandbox \
  --disable-infobars \
  --noerrdialogs \
  --start-fullscreen \
  --disable-context-menu \
  --touch-events=enabled \
  http://localhost:3000
