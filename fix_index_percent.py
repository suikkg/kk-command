import re
from urllib.parse import unquote
from pathlib import Path

root = Path('man-mirror')
pattern = re.compile(r'href="sub/([%a-zA-Z0-9]+\.html)"')

html = root/'index.html'
text = html.read_text(encoding='utf-8', errors='ignore')

def repl(m):
    enc = m.group(1)
    decoded = unquote(enc)
    return f'href="sub/{decoded}"'

new = pattern.sub(repl, text)
if new != text:
    html.write_text(new, encoding='utf-8')
    print('updated index')
else:
    print('no change')
