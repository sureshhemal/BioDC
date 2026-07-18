#!/bin/bash
# Launcher for BioDC — activates the Python venv, sets module paths, runs the program.
cd "$(dirname "$0")/V2.2" || exit 1
source ../.venv/bin/activate
PYTHONPATH=Modules:ForceFieldLib python BioDCv2.py
