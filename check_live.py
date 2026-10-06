import json, os, re, time, urllib.request
CH = "UCw-3ZPyFuyVEK7p72f1RcGw"
KEY = os.environ["YT_API_KEY"]
API = "https://www.googleapis.com/youtube/v3/"
def get(u): return urllib.request.urlopen(u, timeout=20).read().decode()
def details(ids):
    out = []
    for i in range(0, len(ids), 50):
        out += json.loads(get(f"{API}videos?part=liveStreamingDetails&id={','.join(ids[i:i+50])}&key={KEY}")).get("items", [])
    return out

# 1) is the station live right now? (cheap: RSS + 1 API unit)
feed = re.findall(r"<yt:videoId>([\w-]{11})</yt:videoId>", get(f"https://www.youtube.com/feeds/videos.xml?channel_id={CH}"))[:15]
live = None
for v in details(feed):
    d = v.get("liveStreamingDetails")
    if d and d.get("actualStartTime") and not d.get("actualEndTime"):
        live = live or v["id"]

# 2) catalog of ALL finished livestreams, rebuilt once a day
old = {"updated": 0, "ids": []}
try: old = json.load(open("replays.json"))
except Exception: pass
ids = old["ids"]
if time.time() - old["updated"] > 86400 or not ids:
    vids, tok = [], ""
    for _ in range(40):  # up to ~2000 videos
        d = json.loads(get(f"{API}playlistItems?part=contentDetails&maxResults=50&playlistId=UU{CH[2:]}&key={KEY}" + (f"&pageToken={tok}" if tok else "")))
        vids += [i["contentDetails"]["videoId"] for i in d["items"]]
        tok = d.get("nextPageToken")
        if not tok: break
    ids = [v["id"] for v in details(vids) if v.get("liveStreamingDetails", {}).get("actualEndTime")]
    json.dump({"updated": int(time.time()), "ids": ids}, open("replays.json", "w"))

status = {"live": bool(live), "videoId": live or (ids[0] if ids else None), "replay": ids[0] if ids else None}
json.dump(status, open("status.json", "w"))
print(status, len(ids), "past livestreams")
