#!/bin/bash
# Stop the local server started by scripts/serve_local.sh.
cd "$(dirname "$0")/.."
PIDFILE=.local_server.pid
if [ -f "$PIDFILE" ]; then
  pid=$(cat "$PIDFILE")
  if kill -0 "$pid" 2>/dev/null; then kill "$pid" && echo "stopped local server (pid $pid)"; else echo "server was not running (stale pid file)"; fi
  : > "$PIDFILE"   # empty the pid file (nothing is deleted)
else
  echo "no pid file: local server not started by serve_local.sh"
fi
