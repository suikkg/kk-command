import re
from pathlib import Path

root = Path('man-mirror')
patterns = [
    (re.compile(r'https?://man\.niaoge\.com'), '.'),
]
abs_re = re.compile(r'(href|src)="/(?!/)')  # leading slash not protocol

for html in root.rglob('*.html'):
    text = html.read_text(encoding='utf-8', errors='ignore')
    orig = text
    for pat, repl in patterns:
        text = pat.sub(repl, text)
    text = abs_re.sub(r'\1="./', text)
    if text != orig:
        html.write_text(text, encoding='utf-8')
