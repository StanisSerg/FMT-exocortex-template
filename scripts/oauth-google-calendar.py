#!/usr/bin/env python3
"""OAuth callback server for Google Calendar (desktop app / loopback)."""
import http.server
import json
import os
import socketserver
import subprocess
import sys
import urllib.parse

socketserver.TCPServer.allow_reuse_address = True

CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID", "")
CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET", "")
PORT = int(os.environ.get("OAUTH_PORT", "8080"))
REDIRECT_URI = f"http://127.0.0.1:{PORT}"
AUTH_CODE = None


class Handler(http.server.BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        pass  # suppress default logging

    def do_GET(self):
        global AUTH_CODE
        parsed = urllib.parse.urlparse(self.path)
        query = urllib.parse.parse_qs(parsed.query)
        code = query.get("code", [None])[0]
        error = query.get("error", [None])[0]

        if error:
            self.send_response(400)
            self.end_headers()
            self.wfile.write(f"Error: {error}".encode())
            AUTH_CODE = f"ERROR:{error}"
            self.server.shutdown()
            return

        if code:
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(
                b"<html><body>"
                b"<h2>Google Calendar authorized!</h2>"
                b"<p>You can close this tab and return to the terminal.</p>"
                b"</body></html>"
            )
            AUTH_CODE = code
            self.server.shutdown()
            return

        self.send_response(400)
        self.end_headers()
        self.wfile.write(b"No code received.")
        AUTH_CODE = "ERROR:no_code"
        self.server.shutdown()


def exchange_code(code: str) -> dict:
    data = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "code": code,
        "redirect_uri": REDIRECT_URI,
        "grant_type": "authorization_code",
    }
    import urllib.request
    req = urllib.request.Request(
        "https://oauth2.googleapis.com/token",
        data=urllib.parse.urlencode(data).encode(),
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode())


def main():
    if not CLIENT_ID or not CLIENT_SECRET:
        print("ERROR: GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET must be set.")
        sys.exit(1)

    # Build authorization URL
    params = {
        "client_id": CLIENT_ID,
        "redirect_uri": REDIRECT_URI,
        "scope": "https://www.googleapis.com/auth/calendar.readonly",
        "response_type": "code",
        "access_type": "offline",
        "prompt": "consent",
    }
    auth_url = "https://accounts.google.com/o/oauth2/v2/auth?" + urllib.parse.urlencode(params)

    print("========================================")
    print("  Google Calendar OAuth")
    print("========================================")
    print("")
    print("1. Open this URL in your browser:")
    print(f"   {auth_url}")
    print("")
    print("2. Sign in with Google and click 'Allow'.")
    print("   (If you see 'This app isn't verified' → Advanced → Go to unsafe → Allow)")
    print("")
    print("3. Return here after the browser shows 'authorized'.")
    print("")
    print(f"Listening on {REDIRECT_URI} ...")
    print("")

    with socketserver.TCPServer(("127.0.0.1", PORT), Handler) as httpd:
        httpd.allow_reuse_address = True
        httpd.serve_forever()

    if AUTH_CODE and AUTH_CODE.startswith("ERROR:"):
        print(f"Failed: {AUTH_CODE}")
        sys.exit(1)

    if not AUTH_CODE:
        print("ERROR: No authorization code received.")
        sys.exit(1)

    print("Authorization code received. Exchanging for tokens...")
    tokens = exchange_code(AUTH_CODE)

    refresh_token = tokens.get("refresh_token", "")
    access_token = tokens.get("access_token", "")
    expires_in = tokens.get("expires_in", "")

    if not refresh_token:
        print("ERROR: No refresh_token in response.")
        print("Response:", json.dumps(tokens, indent=2))
        sys.exit(1)

    secrets_path = os.path.expanduser("~/.secrets/google-calendar")
    os.makedirs(os.path.dirname(secrets_path), exist_ok=True)
    with open(secrets_path, "w") as f:
        f.write(f"GOOGLE_CLIENT_ID={CLIENT_ID}\n")
        f.write(f"GOOGLE_CLIENT_SECRET={CLIENT_SECRET}\n")
        f.write(f"GOOGLE_REFRESH_TOKEN={refresh_token}\n")
    os.chmod(secrets_path, 0o600)

    print("")
    print("========================================")
    print("  Success!")
    print("========================================")
    print(f"Saved to: {secrets_path}")
    print(f"Refresh token: {refresh_token[:10]}...")
    print("")
    print("Test:")
    print(f"  bash {os.path.expanduser('~/IWE/scripts/server-calendar.sh')} {os.popen('date +%Y-%m-%d').read().strip()}")


if __name__ == "__main__":
    main()
