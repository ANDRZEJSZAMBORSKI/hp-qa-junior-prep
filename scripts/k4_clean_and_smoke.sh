#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
LOG_DIR="${LOG_DIR:-/tmp/k4_logs}"

echo "==> clean logs in $LOG_DIR"
mkdir -p "$LOG_DIR"
rm -f "$LOG_DIR"/*.log
echo "cleaned"

echo "==> smoke: mock-api (optional if docker available)"
if command -v docker >/dev/null 2>&1; then
  cd "$ROOT"
  docker compose up -d mock-api
  sleep 4
  code="$(curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:1080/ || true)"
  echo "mock-api HTTP: $code"
  if [[ "$code" != "404" && "$code" != "200" ]]; then
    echo "smoke FAIL: unexpected code '$code'"
    docker compose down
    exit 1
  fi
  docker compose down
else
  echo "docker not found — skip container smoke"
fi

echo "==> smoke: pytest non-UI (host)"
cd "$ROOT"
case "$(uname -s)" in
  MINGW*|MSYS*)
    IS_GIT_BASH=1
    ;;
  Linux)
    IS_GIT_BASH=0
    ;;
  *)
    echo "ERROR: unsupported environment"
    exit 1
    ;;
esac
#if [[ "$(uname -s)" == "Linux" ]]; then
#    VENV_PYTHON="python3"
#    VENV_ACTIVATE=".venv/bin/activate"
#else
#    VENV_PYTHON="python"
#    VENV_ACTIVATE=".venv/Scripts/activate"
#fi
if [[ "$IS_GIT_BASH" -eq 1 ]]; then
    VENV_PYTHON="python"
    VENV_ACTIVATE=".venv/Scripts/activate"
else
    VENV_PYTHON="python3"
    VENV_ACTIVATE=".venv/bin/activate"
fi
if [[ -f "$VENV_ACTIVATE" ]]; then
  # shellcheck disable=SC1091
  source "$VENV_ACTIVATE"
else
  "$VENV_PYTHON" -m venv .venv
  source "$VENV_ACTIVATE"
fi
pytest -m "not ui and not selenium and not compose" -q --tb=line -n auto
echo "==> K4 smoke OK"