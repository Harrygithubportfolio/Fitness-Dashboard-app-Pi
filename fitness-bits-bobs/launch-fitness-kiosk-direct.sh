#!/bin/bash

# Set display immediately
export DISPLAY=:0

# Kill desktop environment to save resources
pkill lxpanel
pkill pcmanfm

# Hide cursor immediately
unclutter -idle 0.1 &

# Disable screen blanking
xset s off
xset -dpms
xset s noblank

# Wait for PM2 service (shorter wait since we're skipping desktop load)
sleep 15

# Launch Chromium in kiosk mode immediately
chromium-browser \
  --kiosk \
  --no-sandbox \
  --disable-infobars \
  --disable-session-crashed-bubble \
  --disable-web-security \
  --disable-features=TranslateUI,VizDisplayCompositor \
  --disable-ipc-flooding-protection \
  --noerrdialogs \
  --start-fullscreen \
  --window-position=0,0 \
  --disable-pinch \
  --overscroll-history-navigation=0 \
  --enable-features=OverlayScrollbar \
  --disable-context-menu \
  --touch-events=enabled \
  --disable-translate \
  --disable-background-timer-throttling \
  --disable-backgrounding-occluded-windows \
  --disable-renderer-backgrounding \
  --autoplay-policy=no-user-gesture-required \
  --fast \
  --fast-start \
  --disable-extensions \
  --disable-plugins \
  --disable-default-apps \
  http://localhost:3000 &

# Hide desktop background
xsetroot -solid black
