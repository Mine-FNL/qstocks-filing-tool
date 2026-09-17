#!/usr/bin/env python3
"""CI helper: assert /healthz returns {"status":"ok",...} and exit 0/1.

Used by .github/workflows/ci.yml's app-smoke job. Standalone so a heredoc
embedded in YAML doesn't risk YAML parse errors.
"""

import json
import sys
import urllib.error
import urllib.request

URL = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:18765/healthz"
TIMEOUT = 5

try:
    body = urllib.request.urlopen(URL, timeout=TIMEOUT).read().decode()
except urllib.error.URLError as e:
    print(f"healthz: request failed: {e}", file=sys.stderr)
    sys.exit(2)
except Exception as e:
    print(f"healthz: unexpected error: {e}", file=sys.stderr)
    sys.exit(2)

try:
    j = json.loads(body)
except json.JSONDecodeError as e:
    print(f"healthz: non-JSON body: {body!r} ({e})", file=sys.stderr)
    sys.exit(3)

status = j.get("status")
if status != "ok":
    print(f"healthz: unexpected body: {body!r}", file=sys.stderr)
    sys.exit(4)

print("healthz ok:", j)
sys.exit(0)
