---
layout: post
title: "How I Got Past the DGX Spark Infinite Wi-Fi Setup Loop"
date: 2026-03-22
url: /2026-03-22-How-I-Got-Past-the-DGX-Spark-Infinite-Wi-Fi-Setup-Loop
categories: ["ai""]
tags: [dgx-spark, oobe, unifi, dns, workaround, nvidia]
---

Got a DGX Spark stuck in an endless Wi-Fi setup loop even though ethernet is plugged in? I ran into the same thing. Here's a network-level fix that worked for me, hopefully it helps you get past it and start enjoying your Spark.

## What's Going On

During initial setup, the Spark checks internet connectivity by hitting `connectivity-check.ubuntu.com` over HTTPS. If that fails, it assumes there's no network and dumps you into the Wi-Fi screen, regardless of whether ethernet is working fine. The problem? Those HTTPS endpoints are all dead. I tested all six IPs the domain resolves to, on both HTTP and HTTPS:

```bash
for ip in 185.125.190.97 185.125.190.98 185.125.190.96 91.189.91.96 91.189.91.98 91.189.91.97; do
  echo "--- Testing $ip on port 80 (HTTP) ---"
  curl -s -o /dev/null -w "HTTP %{http_code} in %{time_total}s\n" --max-time 5 \
    --resolve connectivity-check.ubuntu.com:80:$ip http://connectivity-check.ubuntu.com
  echo "--- Testing $ip on port 443 (HTTPS) ---"
  curl -s -o /dev/null -w "HTTP %{http_code} in %{time_total}s\n" --max-time 5 \
    --resolve connectivity-check.ubuntu.com:443:$ip https://connectivity-check.ubuntu.com
done
```

| IP Address | HTTP (port 80) | HTTPS (port 443) |
|---|---|---|
| 185.125.190.97 | 204 in 0.028s | Timeout |
| 185.125.190.98 | 204 in 0.030s | Timeout |
| 185.125.190.96 | 204 in 0.028s | Timeout |
| 91.189.91.96 | 204 in 0.167s | Timeout |
| 91.189.91.98 | 204 in 0.164s | Timeout |
| 91.189.91.97 | 204 in 0.164s | Timeout |

HTTP works everywhere. HTTPS works nowhere. The Spark uses HTTPS. That's the bug.

A [forum thread](https://forums.developer.nvidia.com/t/setup-wizard-loop/364222) suggested overriding DNS to point at a specific IP, but since none of them respond on 443, that won't cut it.

## The Fix
The idea is simple: run a tiny HTTPS server on your local network that returns the expected 204 response, then use a DNS override on your router to point the Spark at it.

### 1. Generate a self-signed cert
On your Mac (or any machine on the same LAN):

```bash
mkdir -p ~/connectivity-fix && cd ~/connectivity-fix
openssl req -x509 -newkey rsa:2048 -keyout key.pem -out cert.pem \
  -days 30 -nodes -subj '/CN=connectivity-check.ubuntu.com'
```

### 2. Start the server
Save this as `server.py`:

```python
from http.server import HTTPServer, BaseHTTPRequestHandler
import ssl
import threading

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(204)
        self.end_headers()
    def log_message(self, format, *args):
        print(f"[{self.server.server_port}] {args[0]}")

http = HTTPServer(('0.0.0.0', 80), Handler)

https = HTTPServer(('0.0.0.0', 443), Handler)
ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
ctx.load_cert_chain('cert.pem', 'key.pem')
https.socket = ctx.wrap_socket(https.socket, server_side=True)

print("Serving HTTP on :80 and HTTPS on :443")
threading.Thread(target=http.serve_forever, daemon=True).start()
https.serve_forever()
```

Then run it:

```bash
sudo python3 server.py
```

### 3. Test it
In another terminal:

```bash
curl -v --resolve connectivity-check.ubuntu.com:80:127.0.0.1 http://connectivity-check.ubuntu.com
curl -vk --resolve connectivity-check.ubuntu.com:443:127.0.0.1 https://connectivity-check.ubuntu.com
```

Both should return `204 No Content`.

### 4. Add a DNS override on your router
You need your router to resolve `connectivity-check.ubuntu.com` to your Mac's local IP instead of the broken upstream servers.

**UniFi Dream Machine SE (Network 10.1.x)**

If you're on UniFi Network 10.1, the DNS settings have moved compared to older versions. The path is:

**Settings → Policy Engine → Policy Table → Create Policy**

Create a DNS **A record** with `connectivity-check.ubuntu.com` pointing to your Mac's IP (e.g. `192.168.1.143`).

> In older UniFi Network versions (8.x – 9.x), this was under Settings → Routing → DNS.

**Other routers:** look for "Local DNS", "DNS Override", or "Static DNS Entries" in your admin panel.

### 5. Verify and reboot
Confirm the override works:

```bash
nslookup connectivity-check.ubuntu.com 192.168.1.1
```

This should return your Mac's IP. Now reboot the DGX Spark — it should sail past the Wi-Fi screen.

## Cleanup
Once setup is done, stop the Python server, delete the DNS override from your router, and remove `~/connectivity-fix`. The connectivity check only runs during initial setup.

## Alternative
If you'd rather patch the Spark directly, [sjug's recovery image patch](https://github.com/sjug/dgx-spark-ethernet-patch) modifies the setup binary to skip the connectivity check entirely. It requires a Linux machine to prepare a patched USB recovery drive.

## Bottom Line
The Out-of-Box Experience (OOBE) insists on validating connectivity over HTTPS, but Canonical's endpoints aren't responding on port 443. Running a local stand-in server and redirecting DNS gets you past it without opening up the Spark. Hopefully NVIDIA updates the OOBE to fall back to HTTP or skip the check when ethernet is already connected.
