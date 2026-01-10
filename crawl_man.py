import re
from urllib.parse import quote
from urllib.request import urlopen
from pathlib import Path

BASE = 'https://man.niaoge.com'
root = Path('man-mirror')
root.mkdir(exist_ok=True)

visited = set()
pending = set(['/', '/par/1','/par/2','/par/3','/par/4','/par/5'])
command_slugs = set()

allowed = re.compile(r'^/[^\s"\#]+$')
slug_re = re.compile(r'href="(/[^\"]+)"')

def save_page(path: str, data: bytes):
    if path in ('', '/'):
        dest_dir = root
    else:
        enc = quote(path.lstrip('/'), safe='/%')
        dest_dir = root / enc
    dest_dir.mkdir(parents=True, exist_ok=True)
    (dest_dir / 'index.html').write_bytes(data)

while pending:
    path = pending.pop()
    if path in visited:
        continue
    visited.add(path)
    req_path = quote(path, safe='/%')
    url = BASE + req_path
    try:
        data = urlopen(url).read()
    except Exception as e:
        print('fail', path, e)
        continue
    save_page(path, data)
    text = data.decode('utf-8', errors='ignore')
    for m in slug_re.finditer(text):
        href = m.group(1)
        if not allowed.match(href):
            continue
        if href.startswith('//') or href.startswith('http'):
            continue
        if href != '/' and href.endswith('/'):
            href = href[:-1]
        if href.startswith('/par/'):
            pending.add(href)
        elif href.startswith('/public'):
            continue
        elif href.count('/') == 1:  # single segment commands
            command_slugs.add(href.lstrip('/'))
            pending.add(href)
        else:
            pending.add(href)

print('pages visited', len(visited))
print('commands', len(command_slugs))

(public_dir := root / 'public').mkdir(exist_ok=True)
assets = ["/public/style.css", "/public/index.css", "/public/main.js", "/public/img/favicon.ico"]
for a in assets:
    try:
        data = urlopen(BASE + a).read()
        target = root / a.lstrip('/')
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
        print('asset', a)
    except Exception as e:
        print('asset fail', a, e)

try:
    jq = urlopen('https://apps.bdimg.com/libs/jquery/1.10.2/jquery.min.js').read()
    (public_dir / 'jquery.min.js').write_bytes(jq)
    print('asset jquery')
except Exception as e:
    print('jq fail', e)

try:
    jqcss = urlopen('https://apps.bdimg.com/libs/jqueryui/1.10.4/css/jquery-ui.min.css').read()
    (public_dir / 'jquery-ui.min.css').write_bytes(jqcss)
    jqjs = urlopen('https://apps.bdimg.com/libs/jqueryui/1.10.4/jquery-ui.min.js').read()
    (public_dir / 'jquery-ui.min.js').write_bytes(jqjs)
    print('asset jquery-ui')
except Exception as e:
    print('jq ui fail', e)

print('done')
