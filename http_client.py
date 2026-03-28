#!/usr/bin/env python3
"""Pure Python HTTP/1.1 client (no urllib)."""
import socket,ssl,sys
def request(method,url,headers=None,body=None,timeout=10):
    if headers is None: headers={}
    proto,rest=url.split("://",1);host_path=rest.split("/",1)
    host=host_path[0];path="/"+host_path[1] if len(host_path)>1 else "/"
    port=443 if proto=="https" else 80
    if ":" in host: host,port=host.rsplit(":",1);port=int(port)
    sock=socket.socket(socket.AF_INET,socket.SOCK_STREAM);sock.settimeout(timeout)
    sock.connect((host,port))
    if proto=="https": ctx=ssl.create_default_context();sock=ctx.wrap_socket(sock,server_hostname=host)
    headers.setdefault("Host",host);headers.setdefault("User-Agent","pyclient/1.0")
    headers.setdefault("Connection","close")
    if body: headers["Content-Length"]=str(len(body))
    req=f"{method} {path} HTTP/1.1\r\n"
    for k,v in headers.items(): req+=f"{k}: {v}\r\n"
    req+="\r\n";sock.sendall(req.encode())
    if body: sock.sendall(body.encode() if isinstance(body,str) else body)
    response=b""
    while True:
        try:
            chunk=sock.recv(4096)
            if not chunk: break
            response+=chunk
        except: break
    sock.close()
    header_end=response.find(b"\r\n\r\n")
    header_str=response[:header_end].decode();body_bytes=response[header_end+4:]
    status_line=header_str.split("\r\n")[0];status_code=int(status_line.split(" ")[1])
    resp_headers={}
    for line in header_str.split("\r\n")[1:]:
        if ": " in line: k,v=line.split(": ",1);resp_headers[k.lower()]=v
    return {"status":status_code,"headers":resp_headers,"body":body_bytes}
if __name__=="__main__":
    r=request("GET","https://example.com")
    assert r["status"]==200
    print(f"Status: {r['status']}, Body: {len(r['body'])} bytes")
    print("HTTP client OK")
