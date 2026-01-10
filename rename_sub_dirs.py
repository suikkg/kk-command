from pathlib import Path
from urllib.parse import unquote
root = Path('man-mirror/sub')
for path in list(root.iterdir()):
    decoded = unquote(path.name)
    if decoded != path.name:
        target = root / decoded
        if target.exists():
            print('skip existing', path, '->', target)
            continue
        print('rename', path, '->', target)
        path.rename(target)
