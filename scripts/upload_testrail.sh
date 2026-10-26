#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

source .env

trcli -n \
  -h "$TESTRAIL_URL" \
  --project "HP QA Junior Prep" \
  -u "$TESTRAIL_EMAIL" \
  -k "$TESTRAIL_API_KEY" \
  parse_junit \
  --suite-id 1 \
  --case-matcher property \
  --title "N2 pytest API client results" \
  -f testrail-results.xml