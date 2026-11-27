import requests
import http.server
import socketserver
import threading
import urllib.parse
import webbrowser
import time

# =====================================================================
# 1. PROVIDER CONFIGURATION (Paste your real IDs from Step 2 here)
# =====================================================================
PROVIDER = {
    "google": {
        "client_id": "<YOUR_CLIENT_ID>",
               "client_secret": "<YOUR_CLIENT_SECRET>",
               "authorize_url": "<YOUR_AUTHORIZE_URL>",
               "token_url": "<YOUR_TOKEN_URL>",
               "user_info_url": "<YOUR_USER_INFO_URL>",
               "scope": "email public_profile"
    },
    "facebook": {
        "client_id": "<YOUR_CLIENT_ID>",
        "client_secret": "<YOUR_CLIENT_SECRET>",
        "authorize_url": "<YOUR_AUTHORIZE_URL>",
        "token_url": "<YOUR_TOKEN_URL>",
        "user_info_url": "<YOUR_USER_INFO_URL>",
        "scope": "email public_profile"
    },
    "twitter": {
        "client_id": "<YOUR_CLIENT_ID>",
        "client_secret": "<YOUR_CLIENT_SECRET>",
        "authorize_url": "<YOUR_AUTHORIZE_URL>",
        "token_url": "<YOUR_TOKEN_URL>",
        "user_info_url": "<YOUR_USER_INFO_URL>",
        "scope": "tweet.read users.read"
    }
}
REDIRECT_URI = "http://localhost:8000/callback"

SUCCESS_HTML = b"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Authentication Successful</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            margin: 0;
            background-color: #111827;
            color: #F9FAFB;
            text-align: center;
        }
        .card {
            background: #1F2937;
            padding: 2rem 2.5rem;
            border-radius: 12px;
            box-shadow: 0 10px 25px rgba(0,0,0,0.3);
        }
        h2 { color: #4ADE80; margin-top: 0; }
        p { color: #D1D5DB; margin-bottom: 0; }
    </style>
</head>
<body>
    <div class="card">
        <h2>Authentication successful!</h2>
        <p>You can close this window. Closing automatically in <span id="countdown">3</span> seconds...</p>
    </div>
    <script>
        let seconds = 3;
        const countdownEl = document.getElementById("countdown");
        const timer = setInterval(() => {
            seconds--;
            if (countdownEl && seconds >= 0) {
                countdownEl.textContent = seconds;
            }
            if (seconds <= 0) {
                clearInterval(timer);
                window.open('', '_self', '');
                window.close();
            }
        }, 1000);
    </script>
</body>
</html>"""


# =====================================================================
# 2. TEMPORARY LOCAL SERVER TO CATCH THE BROWSER REDIRECT
# =====================================================================
class ReusableTCPServer(socketserver.TCPServer):
    allow_reuse_address = True


class OAuthCallbackHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        parsed_path = urllib.parse.urlparse(self.path)
        if parsed_path.path == "/callback":
            query_params = urllib.parse.parse_qs(parsed_path.query)
            self.server.auth_code = query_params.get("code", [None])[0]
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(SUCCESS_HTML)
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        return


def start_sso_login(provider_name, status_callback=None):
    provider = PROVIDER[provider_name]
    auth_url = (
        f"{provider['authorize_url']}?response_type=code"
        f"&client_id={provider['client_id']}"
        f"&redirect_uri={urllib.parse.quote(REDIRECT_URI, safe='')}"
        f"&scope={urllib.parse.quote(provider['scope'])}"
    )
    server = start_local_server()
    try:
        webbrowser.open(auth_url)
        while server.auth_code is None:
            time.sleep(0.1)
        auth_code = server.auth_code
    finally:
        server.shutdown()
        server.server_close()

    token_response = requests.post(
        provider['token_url'],
        data={
            'grant_type': 'authorization_code',
            'code': auth_code,
            'redirect_uri': REDIRECT_URI,
            'client_id': provider['client_id'],
            'client_secret': provider['client_secret'],
        }
    )
    token_response.raise_for_status()
    access_token = token_response.json().get('access_token')

    user_info_response = requests.get(
        provider['user_info_url'],
        headers={'Authorization': f'Bearer {access_token}'}
    )
    user_info_response.raise_for_status()

    if status_callback:
        status_callback("Login Successful! Opening dashboard...", "#4ADE80")

    return user_info_response.json()


def start_local_server():
    server = ReusableTCPServer(("localhost", 8000), OAuthCallbackHandler)
    server.auth_code = None
    threading.Thread(target=server.serve_forever, daemon=True).start()
    return server
