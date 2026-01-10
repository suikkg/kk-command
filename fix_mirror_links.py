import re
from pathlib import Path
from urllib.parse import quote, unquote

root = Path('man-mirror')
attrs = ['href', 'src']
attr_re = re.compile(r'(href|src)="(/[^"#]*)"')

for html in root.rglob('*.html'):
    if not html.is_file():
        continue
    text = html.read_text(encoding='utf-8', errors='ignore')
    orig = text
    def repl(m):
        attr, path = m.groups()
        if path.startswith('//') or path.startswith('http://') or path.startswith('https://'):
            return m.group(0)
        decoded = unquote(path)
        prefixed = '/man-mirror' + decoded
        if prefixed.endswith('/'):
            final_path = prefixed
        else:
            tail = prefixed.rsplit('/', 1)[-1]
            if '.' in tail:
                final_path = prefixed
            else:
                final_path = prefixed + '/'
        encoded = quote(final_path, safe='/%._-')
        return f'{attr}="{encoded}"'
    text = attr_re.sub(repl, text)
    if text != orig:
        html.write_text(text, encoding='utf-8')
        print('fixed', html)
