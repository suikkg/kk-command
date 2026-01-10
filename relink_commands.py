import re
from pathlib import Path
from urllib.parse import unquote
root = Path('man-mirror')
commands = {p.name for p in root.iterdir() if p.is_dir() and (p/'index.html').exists() and p.name not in {'sub','public','download','shell-script','shell-regex','docs'}}
pattern = re.compile(r'href="\./sub/([^"/]+)/([^"/]+)/"')
for html in root.rglob('*.html'):
    if not html.is_file():
        continue
    txt = html.read_text(encoding='utf-8', errors='ignore')
    def repl(m):
        sub, cmd = m.groups()
        decoded_cmd = unquote(cmd)
        if decoded_cmd in commands:
            return f'href="../{decoded_cmd}/"'
        # also try encoded name as-is
        if cmd in commands:
            return f'href="../{cmd}/"'
        return m.group(0)
    new = pattern.sub(repl, txt)
    if new != txt:
        html.write_text(new, encoding='utf-8')
