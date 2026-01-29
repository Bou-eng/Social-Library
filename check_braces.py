import os

ROOT = os.path.dirname(os.path.dirname(__file__))
extensions = ['.html', '.js', '.css']
bad = []
for dirpath, dirs, files in os.walk(ROOT):
    # skip virtualenv
    if 'venv' in dirpath.split(os.sep):
        continue
    for fn in files:
        if any(fn.endswith(ext) for ext in extensions):
            path = os.path.join(dirpath, fn)
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    s = f.read()
            except Exception:
                continue
            open_count = s.count('{')
            close_count = s.count('}')
            if open_count != close_count:
                bad.append((path, open_count, close_count))

if not bad:
    print('No curly-brace mismatches found in .html/.js/.css files.')
else:
    print('Files with mismatched { / } counts:')
    for p, o, c in bad:
        print(f"{p}: {{={o}, }}={c}")
