"""Post one slot of a day's Sky & Season content to Instagram via the official
Instagram API with Instagram Login (graph.instagram.com).

schedule/<date>.json (written by Claude after Stanley's Sunday review):
  {"date", "status",
   "morning": {"type": "carousel", "slides": [...jpg], "caption": "..."}   # or "reel" with "video"
   "stories": [...jpg],                                                     # go out with the morning slot
   "evening": {...same shape...}}                                           # optional
  Older days use {"reel", "caption", "stories"} and still work.
posted/<date>.json records what went out (idempotent; safe to retry).

Instagram's API cannot schedule, but an uploaded container stays valid for 24 hours. Scheduled runs
start hours early, upload and let Instagram process everything, then wait and publish at exactly
PUBLISH_AT. A run that starts late publishes straight away. Just before publishing, the run re-reads
the newest schedule and markers from origin/main, so a late hold, caption edit or another run's post
is respected.

Env: IG_ACCESS_TOKEN, SLOT=morning|evening|monthly (monthly = schedule/monthly/<date>.json, approved only), DATE (default today SGT), DRY_RUN, MEDIA_BASE (comma list,
may contain {sha}), PUBLISH_AT (HH:MM Singapore).
"""
import datetime, json, os, subprocess, time, urllib.parse, urllib.request, urllib.error

API = "https://graph.instagram.com/v23.0"
TOKEN = os.environ.get("IG_ACCESS_TOKEN", "").strip()
DRY = os.environ.get("DRY_RUN", "") in ("1", "true", "yes")
SLOT = (os.environ.get("SLOT") or "morning").strip()
SGT = datetime.timezone(datetime.timedelta(hours=8))
DATE = (os.environ.get("DATE") or "").strip() or datetime.datetime.now(SGT).date().isoformat()
PUBLISH_AT = (os.environ.get("PUBLISH_AT") or "").strip()


def _head_sha():
    try:
        return subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
    except Exception:
        return ""


MEDIA_BASES = [b.strip().rstrip("/").replace("{sha}", _head_sha() or "main")
               for b in os.environ["MEDIA_BASE"].split(",") if b.strip()]
UID = None


def call(method, path, **params):
    params["access_token"] = TOKEN
    data = urllib.parse.urlencode(params).encode()
    url = f"{API}/{path}"
    req = urllib.request.Request(url + "?" + data.decode()) if method == "GET" else urllib.request.Request(url, data=data, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        body = e.read().decode(errors="replace")
        raise SystemExit(f"Instagram API error {e.code} on {method} {path}: {body.replace(TOKEN, '***') if TOKEN else body}")


def wait_ready(cid, what):
    for _ in range(60):  # up to ~10 minutes
        st = call("GET", cid, fields="status_code,status")
        if st.get("status_code") == "FINISHED":
            return
        if st.get("status_code") in ("ERROR", "EXPIRED"):
            raise SystemExit(f"{what}: Instagram could not process the media: {st}")
        time.sleep(10)
    raise SystemExit(f"{what}: still processing after 10 minutes")


def with_hosts(make, what):
    """make(base_url) -> container id; tries each public media host in turn."""
    last = None
    for base in MEDIA_BASES:
        try:
            cid = make(base)
            wait_ready(cid, what)
            print(f"{what}: uploaded and processed (container {cid})")
            return cid
        except SystemExit as e:
            last = e
            print(f"{what}: host {base} failed ({e}); trying next host")
    raise last


def prepare_item(item, caption, what):
    if item["type"] == "reel":
        def make(b):
            extra = {"cover_url": f"{b}/{item['cover']}"} if item.get("cover") else {}
            return call("POST", f"{UID}/media", media_type="REELS", video_url=f"{b}/{item['video']}",
                        caption=caption, share_to_feed="true", **extra)["id"]
        return with_hosts(make, what)
    if item["type"] == "carousel":
        def make(b):
            kids = []
            for s in item["slides"]:
                k = call("POST", f"{UID}/media", image_url=f"{b}/{s}", is_carousel_item="true")["id"]
                wait_ready(k, what + " slide")
                kids.append(k)
            return call("POST", f"{UID}/media", media_type="CAROUSEL", children=",".join(kids), caption=caption)["id"]
        return with_hosts(make, what)
    if item["type"] == "image":
        return with_hosts(lambda b: call("POST", f"{UID}/media", image_url=f"{b}/{item['slides'][0]}", caption=caption)["id"], what)
    raise SystemExit(f"{what}: unknown post type {item['type']}")


def prepare_story(img, what):
    return with_hosts(lambda b: call("POST", f"{UID}/media", media_type="STORIES", image_url=f"{b}/{img}")["id"], what)


def _norm(text):
    return " ".join((text or "").split())[:120]


def _ts(t):
    return datetime.datetime.strptime(t, "%Y-%m-%dT%H:%M:%S%z")


def existing_post(caption, hours=36):
    """The oldest feed post from the last `hours` whose caption matches: proof it is already live.
    Instagram sometimes answers media_publish with an error (e.g. 2207051 "action is blocked") although
    the post went live; without this check every retry made a duplicate (19 Oct 2026: three carousels)."""
    if not caption:
        return None
    try:
        rows = call("GET", f"{UID}/media", fields="id,caption,permalink,timestamp", limit="25").get("data", [])
    except SystemExit as e:
        print(f"could not list recent posts ({e})"); return None
    since = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(hours=hours)
    hits = [r for r in rows if _norm(r.get("caption")) == _norm(caption) and _ts(r["timestamp"]) >= since]
    if not hits:
        return None
    r = min(hits, key=lambda r: r["timestamp"])
    return {"id": r["id"], "permalink": r.get("permalink", ""), "found": True}


def new_story_since(t0, known_ids):
    try:
        rows = call("GET", f"{UID}/stories", fields="id,permalink,timestamp").get("data", [])
    except SystemExit as e:
        print(f"could not list live stories ({e})"); return None
    for r in sorted(rows, key=lambda r: r["timestamp"]):
        if r["id"] not in known_ids and _ts(r["timestamp"]) >= t0 - datetime.timedelta(seconds=90):
            return {"id": r["id"], "permalink": r.get("permalink", ""), "found": True}
    return None


def finish(cid, what, caption=None, done=None):
    """Publish one container. If Instagram answers with an error, check whether it went live anyway.
    Returns the marker entry, or None when it really did not publish."""
    t0 = datetime.datetime.now(datetime.timezone.utc)
    try:
        m = call("POST", f"{UID}/media_publish", creation_id=cid)["id"]
        link = call("GET", m, fields="permalink").get("permalink", "")
        print(f"published {what}: {m} {link}")
        return {"id": m, "permalink": link}
    except SystemExit as e:
        print(f"{what}: publish answered with an error: {e}")
    for _ in range(3):  # give Instagram a moment, then look for the post
        time.sleep(20)
        if what.startswith("story"):
            known = {v.get("id") for v in (done or {}).values() if isinstance(v, dict)}
            hit = new_story_since(t0, known)
        else:
            hit = existing_post(caption, hours=1)
        if hit:
            print(f"{what}: it went live despite the error: {hit['id']} {hit['permalink']}")
            return hit
    print(f"{what}: not live; leaving it for the next run")
    return None


def latest_from_origin(path):
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
    print(f"ready; waiting until {target:%Y-%m-%d %H:%M} Singapore time ({(target - now).total_seconds() / 60:.0f} min)")
    while True:
        left = (target - datetime.datetime.now(SGT)).total_seconds()
        if left <= 0:
            return
        time.sleep(min(left, 300) if left > 1 else 0.2)


def normalise(s):
    if "reel" in s and "morning" not in s:  # older schedule shape
        s["morning"] = {"type": "reel", "video": s["reel"], "caption": s.get("caption", "")}
    return s


def files_of(item):
    return ([item["video"]] + ([item["cover"]] if item.get("cover") else [])) if item["type"] == "reel" else item["slides"]


def main():
    global UID
    if not TOKEN:
        raise SystemExit("IG_ACCESS_TOKEN secret is missing")
    me = call("GET", "me", fields="user_id,username")
    UID = me["user_id"]
    print(f"account @{me.get('username')} ({UID}); date {DATE}; slot {SLOT}")

    monthly = SLOT == "monthly"   # The Month Ahead: its own file and marker, posts only when approved
    # "posted" = the morning went out and the review page says so; the evening slot must still run
    # (the posted/ markers and the already-live check stop any repeat).
    OK = ("approved",) if monthly else ("pending", "approved", "posted")
    sched_path = f"schedule/monthly/{DATE}.json" if monthly else f"schedule/{DATE}.json"
    if not os.path.exists(sched_path):
        print(f"no {sched_path}; nothing to post"); return
    s = normalise(json.load(open(sched_path, encoding="utf-8")))
    if s.get("status", "pending") not in OK:
        print(f"status is '{s.get('status')}'; not posting"); return
    item = s.get(SLOT)
    if item and item.get("status") in ("review", "hold", "changes"):
        print(f"{SLOT} item is '{item.get('status')}' (waiting for Stanley's approval); not posting it")
        item = None
    stories = s.get("stories", []) if SLOT in ("morning", "monthly") else []
    if not item and not stories:
        print(f"nothing scheduled for the {SLOT} slot"); return
    post_key = "reel" if (SLOT == "morning" and item and item["type"] == "reel") else SLOT
    caption = (item or {}).get("caption", "").strip()
    if item and (not caption or "#" not in caption):
        raise SystemExit("caption or hashtags missing; refusing to post (house rule)")
    missing = [p for p in (files_of(item) if item else []) + stories if not os.path.exists(p)]
    if missing:
        raise SystemExit(f"missing media files: {missing}")
    marker_path = f"posted/monthly/{DATE}.json" if monthly else f"posted/{DATE}.json"
    done = json.load(open(marker_path)) if os.path.exists(marker_path) else {}
    if DRY:
        if item:
            print("already live with this caption:", existing_post(caption) or "no")
        print("dry run OK:", post_key, item and item["type"], files_of(item) if item else [], "stories:", stories)
        print("publish time:", PUBLISH_AT or "immediately"); return

    # 0. Never post the same thing twice: if a post with this caption is already live, record it.
    if item and not done.get(post_key):
        hit = existing_post(caption)
        if hit:
            print(f"{post_key} is already live ({hit['permalink']}); recording it instead of posting again")
            done[post_key] = hit
            done.setdefault("postedAt", datetime.datetime.now(SGT).isoformat(timespec="seconds"))
            if SLOT == "evening":
                done.setdefault("eveningAt", datetime.datetime.now(SGT).isoformat(timespec="seconds"))
            os.makedirs(os.path.dirname(marker_path), exist_ok=True); json.dump(done, open(marker_path, "w"), indent=1)

    # 1. Upload everything early and let Instagram process it.
    todo = []
    if item and not done.get(post_key):
        todo.append((post_key, prepare_item(item, caption, f"{SLOT} {item['type']}")))
    for i, img in enumerate(stories, 1):
        if not done.get(f"story{i}"):
            todo.append((f"story{i}", prepare_story(img, f"story{i}")))
    if not todo:
        print("already posted for", DATE, SLOT); return

    # 2. Wait for the publish time.
    wait_until_publish_time()

    # 3. Last check against the newest repo state.
    pub_caption = caption
    if PUBLISH_AT:
        remote_done = latest_from_origin(marker_path)
        if remote_done:
            done.update(remote_done)
            todo = [t for t in todo if not remote_done.get(t[0])]
            if not todo:
                print("another run already posted this slot; stopping"); return
        latest = latest_from_origin(sched_path)
        if latest:
            latest = normalise(latest)
            if latest.get("status", "pending") not in OK:
                print(f"status changed to '{latest.get('status')}'; not posting"); return
            if (latest.get(SLOT) or {}).get("status") in ("review", "hold", "changes") and any(k == post_key for k, _ in todo):
                print(f"{SLOT} item was put on hold; skipping it")
                todo = [t for t in todo if t[0] != post_key]
                if not todo: return
            new_cap = ((latest.get(SLOT) or {}).get("caption") or "").strip()
            if item and new_cap and "#" in new_cap and new_cap != caption and any(k == post_key for k, _ in todo):
                print("caption was edited since upload; re-uploading with the new caption")
                pub_caption = new_cap
                todo = [(k, prepare_item(item, new_cap, f"{SLOT} {item['type']}") if k == post_key else c) for k, c in todo]

    # 4. Publish: the post first, then stories in order. A failed item never stops the rest
    #    (on 19 Oct the stories were lost because the carousel's error ended the run).
    failed = []
    for key, cid in todo:
        if key == post_key:
            hit = existing_post(pub_caption) or (existing_post(caption) if pub_caption != caption else None)
            if hit:
                print(f"{key} is already live ({hit['permalink']}); not posting again")
            res = hit or finish(cid, key, caption=pub_caption, done=done)
        else:
            res = finish(cid, key, done=done)
            time.sleep(5)
        if not res:
            failed.append(key); continue
        done[key] = res
        if key == post_key:
            done.setdefault("postedAt", datetime.datetime.now(SGT).isoformat(timespec="seconds"))
            if SLOT == "evening":
                done["eveningAt"] = datetime.datetime.now(SGT).isoformat(timespec="seconds")
        os.makedirs(os.path.dirname(marker_path), exist_ok=True); json.dump(done, open(marker_path, "w"), indent=1)
    if failed:
        raise SystemExit(f"not published: {failed} (the next run retries only these)")
    print("all done for", DATE, SLOT)


if __name__ == "__main__":
    main()
