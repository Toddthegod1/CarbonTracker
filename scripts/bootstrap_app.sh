#!/usr/bin/env bash
set -euo pipefail


sudo apt-get update
sudo apt-get install -y nginx python3-venv python3-pip postgresql-client


sudo mkdir -p /opt/carbon-tracker && sudo chown ubuntu:ubuntu /opt/carbon-tracker
cd /opt/carbon-tracker


python3 -m venv .venv
source .venv/bin/activate


# assume repo already cloned to /opt/carbon-tracker
pip install -r requirements.txt


# systemd
sudo cp deploy/app.service /etc/systemd/system/


# nginx
sudo cp deploy/nginx.conf /etc/nginx/sites-available/carbon
sudo ln -sf /etc/nginx/sites-available/carbon /etc/nginx/sites-enabled/carbon
sudo rm -f /etc/nginx/sites-enabled/default || true


sudo systemctl daemon-reload
sudo systemctl enable --now app
sudo systemctl restart nginx