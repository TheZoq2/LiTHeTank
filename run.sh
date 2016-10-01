#!/bin/bash

echo "Starting server..."
gnome-terminal -e server/main.py
echo "Starting client 1, 2 and 3..."
gnome-terminal -e client/main.py
gnome-terminal -e client/main.py
gnome-terminal -e client/main.py
