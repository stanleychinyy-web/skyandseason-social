"""Post one day's Daily Reflection (reel + stories) to Instagram via the official
Instagram API with Instagram Login (graph.instagram.com).

Reads   schedule/<date>.json   (written by Claude after Stanley's Sunday review)
Writes  posted/<date>.json     (marker; makes every run idempotent)

Env: IG_ACCESS_TOKEN (secret), DATE (optional YYYY-MM-DD, default = today in Singapore),
     DRY_RUN=1 (check token + files, post nothing), MEDIA_BASE (public URL prefix),
     PUBLISH_AT (optional HH:MM Singapore time, e.g. 06:00).

Instagram's API cannot schedule a post, but an uploaded media container stays valid for
24 hours. So scheduled runs start hours early, upload and let Instagram process everything,
then wait and press "publish" at exactly PUBLISH_AT. A run that starts after PUBLISH_AT
publishes straight away: a day is never skipped. Just before publishing, the run re-reads
the latest schedule from origin/main so a late hold, caption edit, or another run's
posted marker is respected.
"""
import datetime, json, os, subprocess, sys, time, urllib.parse, urllib.request, urllib.error

API = "https://graph.instagram.com/v23.0"
TOKEN = os.environ.get("IG_ACCESS_TOKEN", "").strip()
DRY = os.environ.get("DRY_RUN", "") in ("1", "true", "yes")
SGT = datetime.timezone(datetime.timedelta(hours=8))
DATE = (os.environ.get("DATE") or "").strip() or datetime.datetime.now(SGT).date().isoformat()
PUBLISH_AT = (os.environ.get("PUBLISH_AT") or "").strip()
def _head_sha():
    try:
        return subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
    except Exception:
        return ""


# MEDIA_BASE may contain {sha}: replaced by the checked-out commit, so media URLs match the files read here.
MEDIA_BASES = [b.strip().rstrip("/").replace("{sha}", _head_sha() or "main")
               for b in os.environ["MEDIA_BASE"].split(",") if b.strip()]


uid_global = None


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


def prepare(uid, params, what, rel):
    """Create a media container and wait until Instagram has processed it.
    Tries each public media host in turn if Instagram can't fetch one."""
    last = None
    for base in MEDIA_BASES:
        p = dict(params)
        p["video_url" if params.get("media_type") == "REELS" else "image_url"] = f"{base}/{rel}"
        try:
            c = call("POST", f"{uid}/media", **p)["id"]
            wait_ready(c, what)
            print(f"{what}: uploaded and processed (container {c})")
            return c
        except SystemExit as e:
            last = e
            print(f"{what}: host {base} failed ({e}); trying next host")
    raise last


def finish(container_id, what):
    m = call("POST", f"{uid_global}/media_publish", creation_id=container_id)["id"]
    link = call("GET", m, fields="permalink").get("permalink", "")
    print(f"published {what}: {m} {link}")
    return {"id": m, "permalink": link}


def latest_from_origin(path):
    """Read a file from the newest origin/main (None if absent or git unavailable)."""
    try:
        subprocess.run(["git", "fetch", "-q", "origin", "main"], check=True, timeout=120)
        r = subprocess.run(["git", "show", f"origin/main:{path}"], capture_output=True, text=True)
        return json.loads(r.stdout) if r.returncode == 0 else None
    except Exception as e:  # never let a git hiccup stop the post
        print(f"could not re-check {path} on origin ({e}); using local copy")
        return False


def wait_until_publish_time():
    if not PUBLISH_AT:
        return
    hh, mm = map(int, PUBLISH_AT.split(":"))
    target = datetime.datetime.fromisoformat(DATE).replace(hour=hh, minute=mm, tzinfo=SGT)
    now = datetime.datetime.now(SGT)
    if now >= target:
        print(f"{now:%H:%M:%S} is past {PUBLISH_AT}; publishing now")
        return
    print(f"ready; waiting until {target:%Y-%m-%d %H:%M:%S} Singapore time ({(target-now).total_seconds()/60:.0f} min)")
    while True:
        left = (target - datetime.datetime.now(SGT)).total_seconds()
        if left <= 0:
            return
        time.sleep(min(left, 300) if left > 1 else 0.2)


def main():
    if not TOKEN:
        raise SystemExit("IG_ACCESS_TOKEN secret is missing")
    me = call("GET", "me", fields="user_id,username")
    global uid_global
    uid = uid_global = me["user_id"]
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
        print("publish time:", PUBLISH_AT or "immediately")
        return

    # 1. Upload everything early and let Instagram process it.
    todo = []
    if not done.get("reel"):
        todo.append(("reel", {"media_type": "REELS", "caption": caption, "share_to_feed": "true"}, s["reel"]))
    for i, img in enumerate(s.get("stories", []), 1):
        if not done.get(f"story{i}"):
            todo.append((f"story{i}", {"media_type": "STORIES"}, img))
    if not todo:
        print("already posted for", DATE)
        return
    containers = {key: prepare(uid, params, key, rel) for key, params, rel in todo}

    # 2. Wait for the publish time.
    wait_until_publish_time()

    # 3. Last check against the newest repo state (hold set late? caption edited? already posted?)
    if PUBLISH_AT:
        remote_done = latest_from_origin(marker_path)
        if remote_done:
            done.update(remote_done)
            todo = [t for t in todo if not remote_done.get(t[0])]
            if not todo:
                print("another run already posted today; stopping")
                return
        latest = latest_from_origin(sched_path)
        if latest:
            if latest.get("status", "pending") not in ("pending", "approved"):
                print(f"status changed to '{latest.get('status')}' since this run started; not posting")
                return
            new_caption = (latest.get("caption") or "").strip()
            if any(t[0] == "reel" for t in todo) and new_caption and "#" in new_caption and new_caption != caption:
                print("caption was edited since upload; re-uploading reel with the new caption")
                containers["reel"] = prepare(uid, {"media_type": "REELS", "caption": new_caption,
                                                   "share_to_feed": "true"}, "reel", s["reel"])

    # 4. Publish: reel first, then stories in order.
    for key, _, _ in todo:
        done[key] = finish(containers[key], key)
        if key == "reel":
            done["postedAt"] = datetime.datetime.now(SGT).isoformat(timespec="seconds")
        json.dump(done, open(marker_path, "w"), indent=1)
    print("all done for", DATE)


if __name__ == "__main__":
    main()
