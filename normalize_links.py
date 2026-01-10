import re
from pathlib import Path

root = Path('man-mirror')
attr_re = re.compile(r'(href|src)="(/man-mirror/[^"#]*)"')

count = 0
for html in root.rglob('*.html'):
    if not html.is_file():
        continue
    text = html.read_text(encoding='utf-8', errors='ignore')
    new = attr_re.sub(lambda m: f'{m.group(1)}="./{m.group(2)[len("/man-mirror/"):]}"', text)
    if new != text:
        html.write_text(new, encoding='utf-8')
        count += 1

print('normalized files', count)
