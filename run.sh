#!/bin/bash

echo "Starting server..."
gnome-terminal -e "bash -c server/main.py;bash"
echo "Starting client 1, 2 and 3..."
gnome-terminal -e "bash -c client/main.py;bash"
gnome-terminal -e "bash -c client/main.py;bash"
gnome-terminal -e "bash -c client/main.py;bash"
