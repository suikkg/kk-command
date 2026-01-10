import re
from pathlib import Path

root = Path('man-mirror')
# Fix top-level index_files and public/linux.png
(top := root / 'index_files').mkdir(exist_ok=True)
# If missing png, create blank placeholder
png = top / '091549405142313.png'
if not png.exists():
    png.write_bytes(b'')
ln_png = root / 'public/linux.png'
if not ln_png.exists():
    ln_png.write_bytes(b'')

# For sub pages, rewrite ./public/... to ../public/...
asset_re = re.compile(r'(href|src)="\./public/([^"]+)"')
for html in root.rglob('*.html'):
    if not html.is_file():
        continue
    txt = html.read_text(encoding='utf-8', errors='ignore')
    new = asset_re.sub(lambda m: f'{m.group(1)}="../public/{m.group(2)}"', txt)
    if new != txt:
        html.write_text(new, encoding='utf-8')
