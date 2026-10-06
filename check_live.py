import json, os, re, urllib.request
CH = "UCw-3ZPyFuyVEK7p72f1RcGw"
KEY = os.environ["YT_API_KEY"]
def get(u):
    return urllib.request.urlopen(u, timeout=20).read().decode()
ids = re.findall(r"<yt:videoId>([\w-]{11})</yt:videoId>", get(f"https://www.youtube.com/feeds/videos.xml?channel_id={CH}"))[:15]
api = ("https://www.googleapis.com/youtube/v3/videos?part=liveStreamingDetails"
       f"&id={','.join(ids)}&key={KEY}")
live, replay = None, None
for v in json.loads(get(api)).get("items", []):  # items follow feed order (newest first)
    d = v.get("liveStreamingDetails")
    if not d: continue
    if d.get("actualStartTime") and not d.get("actualEndTime"):
        live = live or v["id"]
    elif d.get("actualEndTime"):
        replay = replay or v["id"]
status = {"live": bool(live), "videoId": live or replay, "replay": replay}
json.dump(status, open("status.json", "w"))
print(status)
