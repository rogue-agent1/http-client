#!/usr/bin/env python3
"""http_client - HTTP/1.1 client from raw sockets."""
import argparse, socket, ssl, re

def http_request(url, method="GET", headers=None, body=None):
    m = re.match(r'(https?)://([^/:]+)(?::(\d+))?(/.*)?' , url)
    if not m: raise ValueError(f"Invalid URL: {url}")
    scheme, host, port, path = m.groups()
    port = int(port) if port else (443 if scheme == 'https' else 80)
    path = path or '/'
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(10)
    if scheme == 'https':
        ctx = ssl.create_default_context()
        sock = ctx.wrap_socket(sock, server_hostname=host)
    sock.connect((host, port))
    req = f"{method} {path} HTTP/1.1\r\nHost: {host}\r\nConnection: close\r\n"
    if headers:
        for k, v in headers.items(): req += f"{k}: {v}\r\n"
    if body:
        req += f"Content-Length: {len(body)}\r\n"
    req += "\r\n"
    sock.sendall(req.encode())
    if body: sock.sendall(body.encode() if isinstance(body, str) else body)
    response = b''
    while True:
        data = sock.recv(8192)
        if not data: break
        response += data
    sock.close()
    header_end = response.find(b'\r\n\r\n')
    resp_headers = response[:header_end].decode(errors='replace')
    resp_body = response[header_end+4:]
    status_line = resp_headers.split('\r\n')[0]
    return status_line, resp_headers, resp_body

def main():
    p = argparse.ArgumentParser(description="HTTP client")
    p.add_argument("url")
    p.add_argument("-X", "--method", default="GET")
    p.add_argument("-H", "--header", action="append", default=[])
    p.add_argument("-d", "--data")
    p.add_argument("-v", "--verbose", action="store_true")
    args = p.parse_args()
    headers = {}
    for h in args.header:
        k, v = h.split(':', 1); headers[k.strip()] = v.strip()
    status, hdrs, body = http_request(args.url, args.method, headers, args.data)
    if args.verbose: print(hdrs); print()
    else: print(status)
    try: print(body.decode())
    except: print(f"[{len(body)} bytes binary]")

if __name__ == "__main__":
    main()
