#!/usr/bin/env bash
set -euo pipefail


sudo apt-get update
sudo apt-get install -y python3-venv python3-pip


sudo mkdir -p /opt/carbon-tracker && sudo chown ubuntu:ubuntu /opt/carbon-tracker
cd /opt/carbon-tracker


python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt


sudo cp deploy/worker.service /etc/systemd/system/


sudo systemctl daemon-reload
sudo systemctl enable --now worker