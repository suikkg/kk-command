import os
from pathlib import Path
root = Path('man-mirror/sub')
removed = []
mapping = []
for p in list(root.iterdir()):
    name = p.name
    try:
        decoded = name.encode('latin-1').decode('utf-8')
    except Exception:
        continue
    if decoded != name:
        target = root / decoded
        if target.exists():
            if p.is_file():
                p.unlink()
                removed.append((name, decoded))
            elif p.is_dir():
                # skip removing dirs to avoid risk
                pass
            mapping.append((name, decoded))

# update html links
html_files = Path('man-mirror').rglob('*.html')
for html in html_files:
    text = html.read_text(encoding='utf-8', errors='ignore')
    orig = text
    for old, new in mapping:
        text = text.replace(old, new)
    if text != orig:
        html.write_text(text, encoding='utf-8')

print('removed files', len(removed))
