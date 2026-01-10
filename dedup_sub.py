import re
from pathlib import Path
from urllib.parse import unquote

root = Path('man-mirror')
sub = root / 'sub'
mapping = []
removed = 0
for p in list(sub.iterdir()):
    name = p.name
    try:
        decoded = name.encode('latin-1').decode('utf-8')
    except Exception:
        continue
    if decoded != name and (sub/decoded).exists():
        p.unlink()
        removed += 1
        mapping.append((name, decoded))
print('removed', removed)

if mapping:
    htmls = root.rglob('*.html')
    for html in htmls:
        txt = html.read_text(encoding='utf-8', errors='ignore')
        orig = txt
        for old, new in mapping:
            txt = txt.replace(old, new)
        if txt != orig:
            html.write_text(txt, encoding='utf-8')
            print('updated', html)
