import re
from urllib.parse import unquote
from pathlib import Path
root = Path('man-mirror')
subs = {unquote(p.name): p.name for p in (root/'sub').iterdir() if p.is_dir()}
attr_re = re.compile(r'(href|src)="\./sub/([^"#/]+)/"')
for html in root.rglob('*.html'):
    if not html.is_file():
        continue
    txt = html.read_text(encoding='utf-8', errors='ignore')
    def repl(m):
        attr, enc = m.groups()
        decoded = unquote(enc)
        if decoded in subs:
            new = f'./sub/{decoded}/'
            return f'{attr}="{new}"'
        return m.group(0)
    new = attr_re.sub(repl, txt)
    if new != txt:
        html.write_text(new, encoding='utf-8')
