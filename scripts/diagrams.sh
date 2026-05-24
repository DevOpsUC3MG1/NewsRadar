#!/bin/bash
# Regenera diagramas PlantUML a PNG
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_ROOT"

pip install plantuml -q

python3 -c "
from plantuml import deflate_and_encode
import requests, os

ARCH_DIR = 'docs/architecture'

# Only process container-diagram (single unified diagram)
for fname in ['container-diagram.puml']:
    puml = os.path.join(ARCH_DIR, fname)
    png = puml.replace('.puml', '.png')

    with open(puml) as f:
        content = f.read()

    encoded = deflate_and_encode(content)
    url = f'http://www.plantuml.com/plantuml/png/{encoded}'

    resp = requests.get(url, timeout=30)
    if resp.status_code == 200 and resp.headers.get('content-type', '').startswith('image/'):
        with open(png, 'wb') as f:
            f.write(resp.content)
        print(f'OK: {png} ({len(resp.content)} bytes)')
    else:
        print(f'FAIL: {png} status={resp.status_code}')
"

echo "=== Diagramas regenerados ==="
