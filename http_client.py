#!/usr/bin/env python3
"""Minimal HTTP client — GET/POST with headers and JSON support."""
import sys, json
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError
def fetch(url, method="GET", data=None, headers=None):
    req = Request(url, method=method)
    if headers:
        for k, v in headers.items(): req.add_header(k, v)
    if data:
        body = json.dumps(data).encode() if isinstance(data, dict) else data.encode()
        req.add_header("Content-Type", "application/json")
        req.data = body
    try:
        resp = urlopen(req, timeout=10)
        return resp.status, dict(resp.headers), resp.read().decode()
    except HTTPError as e: return e.code, dict(e.headers), e.read().decode()
    except URLError as e: return 0, {}, str(e)
def cli():
    if len(sys.argv) < 2: print("Usage: http_client <URL> [POST json_data] [-H k:v]"); sys.exit(1)
    url = sys.argv[1]; method = "GET"; data = None; hdrs = {}
    i = 2
    while i < len(sys.argv):
        if sys.argv[i] == "POST": method = "POST"; data = json.loads(sys.argv[i+1]); i += 2
        elif sys.argv[i] == "-H": k, v = sys.argv[i+1].split(":", 1); hdrs[k.strip()] = v.strip(); i += 2
        else: i += 1
    status, headers, body = fetch(url, method, data, hdrs)
    print(f"  Status: {status}")
    try: print(json.dumps(json.loads(body), indent=2))
    except: print(body[:500])
if __name__ == "__main__": cli()
