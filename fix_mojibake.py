import os
from pathlib import Path

root = Path('man-mirror')
skip_dirs = {'public','index_files','docs','http_','vip','web'}
renames = []

items = sorted(root.rglob('*'), key=lambda p: len(p.parts), reverse=True)
for p in items:
    if any(part in skip_dirs for part in p.relative_to(root).parts[:1]):
        continue
    name = p.name
    try:
        encoded = name.encode('latin-1')
        decoded = encoded.decode('utf-8')
    except (UnicodeEncodeError, UnicodeDecodeError):
        continue
    if decoded != name:
        target = p.with_name(decoded)
        if target.exists():
            print('skip exists', p, '->', target)
            continue
        renames.append((p, target))

print('planned renames', len(renames))
for src, dst in renames:
    dst.parent.mkdir(parents=True, exist_ok=True)
    print('renaming', src, '->', dst)
    src.rename(dst)

mapping = []
for src, dst in renames:
    mapping.append((src.name, dst.name))
    try:
        mapping.append((src.relative_to(root).as_posix(), dst.relative_to(root).as_posix()))
    except ValueError:
        pass

changed = 0
for html in root.rglob('*.html'):
    text = html.read_text(encoding='utf-8', errors='ignore')
    orig = text
    for old, new in mapping:
        text = text.replace(old, new)
    if text != orig:
        html.write_text(text, encoding='utf-8')
        changed += 1
print('html updated', changed)
