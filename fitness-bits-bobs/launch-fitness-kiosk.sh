#!/bin/bash

# Wait for system to fully boot and PM2 to start
sleep 45

# Set display
export DISPLAY=:0

# Hide mouse cursor after 1 second of inactivity
unclutter -idle 1 &

# Disable screen blanking and screensaver
xset s off
xset -dpms
xset s noblank

# Launch Chromium in kiosk mode
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
  http://localhost:3000

# If Chromium exits, restart after 5 seconds
sleep 5
exec $0
