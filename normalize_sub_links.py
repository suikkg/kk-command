from pathlib import Path
from urllib.parse import unquote
import re
root = Path('man-mirror')
sub_map = {unquote(p.name): p.name for p in (root/'sub').iterdir() if p.is_dir()}
pattern = re.compile(r'href="\./sub/([^"/]+)/([^"/]+)/"')
for html in root.rglob('*.html'):
    if not html.is_file():
        continue
    txt = html.read_text(encoding='utf-8', errors='ignore')
    def repl(m):
        sub, cmd = m.groups()
        decoded_sub = unquote(sub)
        real_sub = sub_map.get(decoded_sub, sub)
        target = root / 'sub' / real_sub / cmd
        if target.is_dir():
            return f'href="./sub/{real_sub}/{cmd}/"'
        elif (target.with_suffix('.html')).exists():
            return f'href="./sub/{real_sub}/{cmd}.html"'
        else:
            return m.group(0)
    new = pattern.sub(repl, txt)
    if new != txt:
        html.write_text(new, encoding='utf-8')
