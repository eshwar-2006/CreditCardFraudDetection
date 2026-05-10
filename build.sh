#!/bin/bash
set -e

echo "Installing pip utilities..."
pip install --upgrade pip setuptools wheel

echo "Installing Python dependencies with pre-built wheels only..."
pip install --only-binary :all: -r requirements.txt || pip install -r requirements.txt

echo "Build complete!"
