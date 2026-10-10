"""Weekly: extend the Instagram long-lived token (valid 60 days, refreshable after 24 h).
If the GH_PAT secret exists, the new token is saved back to the IG_ACCESS_TOKEN secret.
Never prints the token."""
import json, os, subprocess, urllib.parse, urllib.request
tok = os.environ["IG_ACCESS_TOKEN"].strip()
url = "https://graph.instagram.com/refresh_access_token?" + urllib.parse.urlencode(
    {"grant_type": "ig_refresh_token", "access_token": tok})
with urllib.request.urlopen(url, timeout=60) as r:
    d = json.load(r)
new = d["access_token"]
days = int(d.get("expires_in", 0)) // 86400
print(f"token refreshed; valid for {days} more days")
if new != tok:
    if os.environ.get("GH_TOKEN"):
        subprocess.run(["gh", "secret", "set", "IG_ACCESS_TOKEN", "--body", new], check=True,
                       capture_output=True)
        print("saved the new token to the IG_ACCESS_TOKEN secret")
    else:
        raise SystemExit("Instagram returned a new token but no GH_PAT secret is set to save it. "
                         "Generate a fresh token in the Meta app and paste it into the IG_ACCESS_TOKEN secret.")
