"""Post one day's Daily Reflection (reel + stories) to Instagram via the official
Instagram API with Instagram Login (graph.instagram.com).

Reads   schedule/<date>.json   (written by Claude after Stanley's Sunday review)
Writes  posted/<date>.json     (marker; makes every run idempotent)

Env: IG_ACCESS_TOKEN (secret), DATE (optional YYYY-MM-DD, default = today in Singapore),
     DRY_RUN=1 (check token + files, post nothing), MEDIA_BASE (public URL prefix).
"""
import datetime, json, os, sys, time, urllib.parse, urllib.request, urllib.error

API = "https://graph.instagram.com/v23.0"
TOKEN = os.environ.get("IG_ACCESS_TOKEN", "").strip()
DRY = os.environ.get("DRY_RUN", "") in ("1", "true", "yes")
SGT = datetime.timezone(datetime.timedelta(hours=8))
DATE = (os.environ.get("DATE") or "").strip() or datetime.datetime.now(SGT).date().isoformat()
MEDIA_BASES = [b.strip().rstrip("/") for b in os.environ["MEDIA_BASE"].split(",") if b.strip()]


def call(method, path, **params):
    params["access_token"] = TOKEN
    data = urllib.parse.urlencode(params).encode()
    url = f"{API}/{path}"
    if method == "GET":
        req = urllib.request.Request(url + "?" + data.decode())
    else:
        req = urllib.request.Request(url, data=data, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        body = e.read().decode(errors="replace")
        body = body.replace(TOKEN, "***") if TOKEN else body
        raise SystemExit(f"Instagram API error {e.code} on {method} {path}: {body}")


def wait_ready(container_id, what):
    for _ in range(60):  # up to ~10 minutes
        st = call("GET", container_id, fields="status_code,status")
        code = st.get("status_code")
        if code == "FINISHED":
            return
        if code in ("ERROR", "EXPIRED"):
            raise SystemExit(f"{what}: Instagram could not process the media: {st}")
        time.sleep(10)
    raise SystemExit(f"{what}: still processing after 10 minutes")


def publish(uid, params, what, rel=None, url_key=None):
    """Create, wait, publish. Tries each public media host in turn if Instagram can't fetch one."""
    last = None
    for base in MEDIA_BASES:
        if rel:
            params[url_key] = f"{base}/{rel}"
        try:
            c = call("POST", f"{uid}/media", **params)["id"]
            wait_ready(c, what)
            break
        except SystemExit as e:
            last = e
            print(f"{what}: host {base} failed ({e}); trying next host")
    else:
        raise last
    m = call("POST", f"{uid}/media_publish", creation_id=c)["id"]
    link = call("GET", m, fields="permalink").get("permalink", "")
    print(f"published {what}: {m} {link}")
    return {"id": m, "permalink": link}


def main():
    if not TOKEN:
        raise SystemExit("IG_ACCESS_TOKEN secret is missing")
    me = call("GET", "me", fields="user_id,username")
    uid = me["user_id"]
    print(f"account @{me.get('username')} ({uid}); date {DATE}")

    sched_path = f"schedule/{DATE}.json"
    if not os.path.exists(sched_path):
        print(f"no {sched_path}; nothing to post")
        return
    s = json.load(open(sched_path, encoding="utf-8"))
    status = s.get("status", "pending")
    if status not in ("pending", "approved"):
        print(f"status is '{status}'; not posting")
        return
    marker_path = f"posted/{DATE}.json"
    done = json.load(open(marker_path)) if os.path.exists(marker_path) else {}
    caption = s["caption"].strip()
    if not caption or "#" not in caption:
        raise SystemExit("caption or hashtags missing; refusing to post (house rule)")

    for p in [s["reel"]] + s.get("stories", []):
        if not os.path.exists(p):
            raise SystemExit(f"missing media file {p}")
    if DRY:
        print("dry run OK: token works, schedule and media present:", s["reel"], s.get("stories"))
        print("public reel URLs:", [f"{b}/{s['reel']}" for b in MEDIA_BASES])
        return

    if not done.get("reel"):
        done["reel"] = publish(uid, {"media_type": "REELS", "caption": caption, "share_to_feed": "true"},
                               "reel", rel=s["reel"], url_key="video_url")
        done["postedAt"] = datetime.datetime.now(SGT).isoformat(timespec="seconds")
        json.dump(done, open(marker_path, "w"), indent=1)
    for i, img in enumerate(s.get("stories", []), 1):
        key = f"story{i}"
        if done.get(key):
            continue
        done[key] = publish(uid, {"media_type": "STORIES"}, key, rel=img, url_key="image_url")
        json.dump(done, open(marker_path, "w"), indent=1)
    print("all done for", DATE)


if __name__ == "__main__":
    main()
