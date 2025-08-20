#!/bin/bash

# Set display
export DISPLAY=:0

# Hide cursor
unclutter -idle 0.1 &

# Disable screen blanking
xset s off
xset -dpms  
xset s noblank

# Black background
xsetroot -solid black

# Wait for PM2 service
sleep 10

# Launch ONLY the dashboard - nothing else
exec chromium-browser \
  --kiosk \
  --no-sandbox \
  --disable-infobars \
  --noerrdialogs \
  --start-fullscreen \
  --disable-context-menu \
  --touch-events=enabled \
  --disable-session-crashed-bubble \
  --disable-web-security \
  --window-position=0,0 \
  --autoplay-policy=no-user-gesture-required \
  http://localhost:3000
