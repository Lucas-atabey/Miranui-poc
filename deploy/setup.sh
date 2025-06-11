#!/bin/bash
set -e

REGISTRY_KEY="$1"

# Installer Docker (si nécessaire)
if ! command -v docker &> /dev/null; then
  echo "Docker non trouvé. Installation..."
  curl -fsSL https://get.docker.com -o get-docker.sh
  sudo sh get-docker.sh
fi

# Installer Docker Compose (si nécessaire)
if ! command -v docker-compose &> /dev/null; then
  echo "Docker Compose non trouvé. Installation..."
  sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" \
    -o /usr/local/bin/docker-compose
  sudo chmod +x /usr/local/bin/docker-compose
fi

sudo docker login lucas-rex.cr.de-fra.ionos.com -u lucas-git-token -p "$REGISTRY_KEY"

# Construire et démarrer les containers
cd ..

sudo docker-compose pull
sudo docker-compose down || true
sudo docker-compose up -d