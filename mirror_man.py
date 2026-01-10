import re
import sys
from pathlib import Path
from urllib.request import urlopen
from urllib.error import HTTPError, URLError

BASE = "https://man.niaoge.com"
root = Path('man-mirror')
root.mkdir(exist_ok=True)

# helper
def fetch(url: str) -> bytes:
    with urlopen(url) as resp:
        return resp.read()

# download category pages
par_pages = ["/", "/par/1", "/par/2", "/par/3", "/par/4", "/par/5"]
par_html = {}
for p in par_pages:
    url = BASE + p
    try:
        data = fetch(url)
        par_html[p] = data
        (root / f"par{p.strip('/').replace('/', '_') or 'index'}.html").write_bytes(data)
        print("fetched", url)
    except Exception as e:
        print("fail", url, e, file=sys.stderr)

# extract command slugs
slugs = set()
pattern = re.compile(r"href=\"/([A-Za-z0-9_.-]+)\"")
for content in par_html.values():
    for m in pattern.finditer(content.decode('utf-8', errors='ignore')):
        slug = m.group(1)
        if slug and slug not in {'par', 'public', 'about_us', 'shell-script', 'shell-regex'} and '/' not in slug:
            slugs.add(slug)

print("found slugs", len(slugs))

# download public assets
public = root / 'public'
public.mkdir(exist_ok=True)
assets = ["/public/style.css", "/public/index.css", "/public/main.js", "/public/img/favicon.ico"]
for a in assets:
    url = BASE + a
    try:
        data = fetch(url)
        (root / a.lstrip('/')).write_bytes(data)
        print("asset", a)
    except Exception as e:
        print("asset fail", a, e, file=sys.stderr)
# jquery local copy
try:
    jq = fetch("https://apps.bdimg.com/libs/jquery/1.10.2/jquery.min.js")
    (public / 'jquery.min.js').write_bytes(jq)
    print("asset jquery")
except Exception as e:
    print("asset jquery fail", e, file=sys.stderr)

# download each command page
for slug in sorted(slugs):
    url = f"{BASE}/{slug}"
    try:
        html = fetch(url).decode('utf-8', errors='ignore')
    except Exception as e:
        print("fail page", slug, e, file=sys.stderr)
        continue
    # rewrite jquery src to local copy
    html = html.replace("https://apps.bdimg.com/libs/jquery/1.10.2/jquery.min.js", "/public/jquery.min.js")
    # ensure protocol-less forms maybe none
    (root / f"{slug}.html").write_text(html, encoding='utf-8')
    print("saved", slug)

print("done")
