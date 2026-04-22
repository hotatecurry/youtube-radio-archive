from urllib.request import urlopen, Request
import re

url = "https://www.youtube.com/@prohamburger1118"
req = Request(url, headers={"User-Agent": "Mozilla/5.0"})
html = urlopen(req).read().decode()
m = re.search(r'"channelId":"(UC[^"]+)"', html)
print(m.group(1) if m else "取得失敗")