import os
import re
from pathlib import Path
from urllib.parse import unquote

root = Path('man-mirror')
cmd_dirs = {p.name for p in root.iterdir() if p.is_dir() and (p / 'index.html').exists() and p.name not in {'sub','public','download','shell-script','shell-regex','docs'}}

abs_re = re.compile(r'(href|src)="(/man-mirror/[^"#]*)"')
sub_cmd_re = re.compile(r'href="\./([^"/]+)/"')

for html in root.rglob('*.html'):
    if not html.is_file():
        continue
    parent = html.parent
    txt = html.read_text(encoding='utf-8', errors='ignore')
    orig = txt

    # 1) convert absolute /man-mirror/... to relative
    def repl_abs(m):
        attr, url = m.groups()
        target = root / url[len('/man-mirror/'):]
        if target.is_dir() and (target / 'index.html').exists():
            target = target / ''
        try:
            rel = os.path.relpath(target, parent)
        except Exception:
            return m.group(0)
        if target.is_dir() and not rel.endswith('/'):
            rel = rel + '/'
        return f'{attr}="{rel}"'

    txt = abs_re.sub(repl_abs, txt)

    # 2) in sub/* pages, adjust command links ./cmd/ -> ../cmd/
    if html.parts[1] == 'sub':
        def repl_sub(m):
            cmd = unquote(m.group(1))
            if cmd in cmd_dirs:
                return f'href="../{cmd}/"'
            return m.group(0)
        txt = sub_cmd_re.sub(repl_sub, txt)

    if txt != orig:
        html.write_text(txt, encoding='utf-8')
