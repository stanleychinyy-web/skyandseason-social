"""Read-only: print what Instagram reports for given media ids (no changes)."""
import json, os, sys, urllib.parse, urllib.request, urllib.error
T = os.environ["IG_ACCESS_TOKEN"].strip()
for mid in os.environ["MEDIA_IDS"].split(","):
    mid = mid.strip()
    for fields in ["media_type,media_product_type,permalink,timestamp,caption",
                   "copyright_check_information",
                   "is_shared_to_feed,thumbnail_url"]:
        url = f"https://graph.instagram.com/v23.0/{mid}?" + urllib.parse.urlencode({"fields": fields, "access_token": T})
        try:
            d = json.load(urllib.request.urlopen(url, timeout=60))
            d.pop("caption", None); d.pop("thumbnail_url", None)
            print(mid, fields.split(",")[0], json.dumps(d))
        except urllib.error.HTTPError as e:
            print(mid, fields.split(",")[0], "ERROR", e.code, e.read().decode()[:300].replace(T, "***"))
