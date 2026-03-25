import re
import json
import hashlib
import pathlib
import urllib.parse

urls = [
    u.strip()
    for u in pathlib.Path('tmp/all-image-urls.txt').read_text(encoding='utf-8').splitlines()
    if u.strip()
]

manifest = pathlib.Path('assets/original-images-manifest.csv')
mapjson = pathlib.Path('assets/original-images-map.json')

rows = []
mapping = {}

for url in urls:
    parsed = urllib.parse.urlparse(url)
    ext = pathlib.Path(parsed.path).suffix.lower()
    if ext not in {'.jpg', '.jpeg', '.png', '.webp', '.gif', '.avif'}:
        ext = '.bin'

    rel = f"assets/original-images/{hashlib.sha1(url.encode('utf-8')).hexdigest()}{ext}"
    file_path = pathlib.Path(rel)
    status = 'ok' if file_path.exists() and file_path.stat().st_size > 0 else 'failed'

    rows.append((url, rel, status))
    mapping[url] = rel

with manifest.open('w', encoding='utf-8') as file:
    file.write('url,local_path,status\n')
    for url, rel, status in rows:
        file.write(f'"{url}","{rel}","{status}"\n')

mapjson.write_text(json.dumps(mapping, indent=2), encoding='utf-8')

history_html = pathlib.Path('tmp/page-history.html').read_text(encoding='utf-8', errors='ignore')
found = re.findall(r'https://images\.squarespace-cdn\.com[^"\s)<>]+', history_html)

seen = set()
ordered = []
for url in found:
    normalized = url.replace('&amp;', '&').replace('\\u0026', '&')
    if normalized not in seen:
        seen.add(normalized)
        ordered.append(normalized)

pathlib.Path('tmp/history-image-urls.txt').write_text('\n'.join(ordered) + '\n', encoding='utf-8')

failed = sum(1 for _, _, status in rows if status != 'ok')
print(f'rows {len(rows)} failed {failed}')
print(f'history_unique {len(ordered)}')
