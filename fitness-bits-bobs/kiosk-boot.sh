#!/bin/bash

# Wait for system to be ready
sleep 15

# Start X server on display :0 without any window manager
sudo -u pi startx /home/pi/dashboard-only.sh -- :0 vt7 &

# Wait for X to start
sleep 5

exit 0
