from pathlib import Path
from urllib.parse import unquote
import re
root = Path('man-mirror')
subdir = root/'sub'
html = root/'index.html'
text = html.read_text(encoding='utf-8', errors='ignore')
changed=False
for m in re.finditer(r'href="sub/([^"]+\.html)"', text):
    enc = m.group(1)
    dec1 = unquote(enc)
    try:
        dec2 = dec1.encode('latin-1').decode('utf-8')
    except Exception:
        dec2 = dec1
    target = subdir/dec2
    if target.exists() and enc != dec2:
        text = text.replace(f'sub/{enc}', f'sub/{dec2}')
        changed=True
if changed:
    html.write_text(text, encoding='utf-8')
    print('index links updated')
else:
    print('no change')
