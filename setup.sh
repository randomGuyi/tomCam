#!/bin/sh

echo "=== Raspberry Pi camera setup ==="

echo "Updating package lists..."
if sudo apt update; then
    echo "OK: apt update succeeded."
else
    echo "ERROR: apt update failed."
    exit 1
fi

echo "Installing Vim..."
if sudo apt install -y vim; then
    echo "OK: Vim installed."
else
    echo "ERROR: Vim installation failed."
fi

echo "Upgrading installed packages..."
if sudo apt upgrade -y; then
    echo "OK: System upgrade succeeded."
else
    echo "ERROR: System upgrade failed."
fi

echo "Installing Python pip..."
if sudo apt install -y python3-pip; then
    echo "OK: python3-pip installed."
else
    echo "ERROR: python3-pip installation failed."
fi

echo "Installing OpenCV..."
if sudo apt install -y python3-opencv; then
    echo "OK: OpenCV installed."
else
    echo "ERROR: OpenCV installation failed."
fi

echo "Installing Git..."
if sudo apt install -y git; then
    echo "OK: Git installed."
else
    echo "ERROR: Git installation failed."
fi

echo
echo "Available video ports:"
if ls /dev/video* 2>/dev/null; then
    echo "OK: Video device(s) found."
else
    echo "WARNING: No /dev/video* devices found."
fi

echo
echo "Creating camera directory..."

if mkdir -p camera; then
    echo "OK: camera directory ready."
else
    echo "ERROR: Could not create camera directory."
    exit 1
fi

if cd camera; then
    echo "OK: Entered camera directory."
else
    echo "ERROR: Could not enter camera directory."
    exit 1
fi

echo
echo "Cloning project..."

if git clone https://github.com/randomGuyi/tomCam.git; then
    echo "OK: Repository cloned."
else
    echo "ERROR: Git clone failed."
    exit 1
fi

if cd tomCam; then
    echo "OK: Entered tomCam directory."
else
    echo "ERROR: Could not enter tomCam directory."
    exit 1
fi

echo
echo "=== Setup completed successfully ==="
echo "Current directory:"
pwd
