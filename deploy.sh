#!/bin/bash
# Deploy script - pulls latest code and restarts app
sudo cp /home/ubuntu/deploy/server.js /opt/app/server.js
sudo systemctl restart app
sleep 2
curl -f http://localhost/health && echo "DEPLOY OK" || echo "DEPLOY FAILED"
