#!/bin/bash
# Baut die Test-Seite und startet einen lokalen Webserver:  bash test-env/serve.sh   (Port: PORT=8082)
set -e
cd "$(dirname "$0")"
node build.js
PORT="${PORT:-8082}"
echo "Arbeitsumgebung läuft auf http://localhost:$PORT/index.html  (Beenden mit Strg+C)"
cd dist && python3 -m http.server "$PORT"
