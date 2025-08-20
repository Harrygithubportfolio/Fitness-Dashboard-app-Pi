#!/bin/bash

# Start X server
sudo systemctl start lightdm &

# Wait for X to start
sleep 8

# Set display
export DISPLAY=:0

# Hide cursor immediately
unclutter -idle 0.1 &

# Disable screen blanking
xset s off
xset -dpms
xset s noblank

# Set black background
xsetroot -solid black

# Wait for PM2 to be ready
sleep 10

# Launch dashboard directly - no desktop
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
  http://localhost:3000
