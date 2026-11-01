#!/bin/bash
# LOCAL ONLY launcher: build with the private layer, serve the project on 127.0.0.1:8765, open the browser.
# Binds to 127.0.0.1 only (never 0.0.0.0). Stop with scripts/stop_local.sh.
set -e
cd "$(dirname "$0")/.."
PORT=8765
PIDFILE=.local_server.pid
if [ -f "$PIDFILE" ] && kill -0 "$(cat "$PIDFILE")" 2>/dev/null; then
  echo "already running (pid $(cat "$PIDFILE")) at http://127.0.0.1:$PORT/"
else
  python3 -I scripts/build_data.py --private | tail -12
  nohup python3 -m http.server $PORT --bind 127.0.0.1 > .local_server.log 2>&1 &
  echo $! > "$PIDFILE"
  sleep 1
  echo "serving http://127.0.0.1:$PORT/ (pid $(cat "$PIDFILE"), 127.0.0.1 only; stop with scripts/stop_local.sh)"
fi
open "http://127.0.0.1:$PORT/" 2>/dev/null || true
