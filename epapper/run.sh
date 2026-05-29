#!/usr/bin/env sh
set -eu

export OPTIONS_JSON=/data/options.json
export HA_WS_URL="ws://supervisor/core/websocket"
# SUPERVISOR_TOKEN is auto-injected by HA Supervisor

exec python -m epapper
