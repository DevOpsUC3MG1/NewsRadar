#!/bin/bash
set -e

# Pull latest images if running in CI with registry
if [ -n "$CI" ]; then
  docker compose pull
fi

docker compose up -d --build
