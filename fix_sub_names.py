import os
from pathlib import Path

root = Path('man-mirror')
subdir = root / 'sub'
renames = []
for p in subdir.iterdir():
    name = p.name
    try:
        decoded = name.encode('latin-1').decode('utf-8')
    except (UnicodeEncodeError, UnicodeDecodeError):
        continue
    if decoded != name:
        target = subdir / decoded
        if target.exists():
            print('skip existing', p, '->', target)
            continue
        renames.append((p, target))

# apply renames
for src, dst in renames:
    print('renaming', src.name, '->', dst.name)
    src.rename(dst)

# update references in all html files under man-mirror
mapping = [(src.name, dst.name) for src, dst in renames]
if mapping:
    for html in root.rglob('*.html'):
        text = html.read_text(encoding='utf-8', errors='ignore')
        orig = text
        for old, new in mapping:
            text = text.replace(old, new)
        if text != orig:
            html.write_text(text, encoding='utf-8')
            print('updated', html)
else:
    print('no renames needed')
