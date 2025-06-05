#!/bin/bash
set -e

# Installer Docker (si nécessaire)
if ! command -v docker &> /dev/null; then
  echo "Docker non trouvé. Installation..."
  curl -fsSL https://get.docker.com -o get-docker.sh
  sudo sh get-docker.sh
fi

# Construire et démarrer les containers
cd ..
docker-compose down || true
docker-compose up -d --build
