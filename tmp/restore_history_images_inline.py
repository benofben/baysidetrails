import json
import re
from pathlib import Path

root = Path('/Users/ben/github/benofben/baysidetrails')
history_path = root / 'history.html'
source_path = root / 'tmp' / 'page-history.html'
map_path = root / 'assets' / 'original-images-map.json'
ref_path = root / 'tmp' / 'ref-history.html'

current = history_path.read_text(encoding='utf-8')
source = source_path.read_text(encoding='utf-8', errors='ignore')
url_map = json.loads(map_path.read_text(encoding='utf-8'))
ref_html = ref_path.read_text(encoding='utf-8', errors='ignore')

nav_match = re.search(r'(<nav>[\s\S]*?</nav>)', current)
footer_match = re.search(r'(<footer>[\s\S]*?</footer>)', current)
if not nav_match or not footer_match:
    raise SystemExit('Could not locate nav/footer in history.html')

nav = nav_match.group(1)
footer = footer_match.group(1)

ref_images = {
    u.replace('&amp;', '&').replace('\\u0026', '&').split('?format=')[0]
    for u in re.findall(r'https://images\.squarespace-cdn\.com/content/v1/[^" ]+', ref_html)
}

text_pattern = re.compile(r'<div class="sqs-html-content" data-sqsp-text-block-content>([\s\S]*?)</div>')
img_pattern = re.compile(r'data-src="(https://images\.squarespace-cdn\.com/content/v1/[^"]+)"')

year_re = re.compile(r'<h2[^>]*>\s*(\d{4})\s*</h2>')
h1_re = re.compile(r'<h1[^>]*>\s*History\s*</h1>', flags=re.I)

items = []
for m in text_pattern.finditer(source):
    items.append((m.start(), 'text', m.group(1)))
for m in img_pattern.finditer(source):
    items.append((m.start(), 'img', m.group(1)))
items.sort(key=lambda x: x[0])

sections = {}
order = []
current_year = None
seen_images_by_year = {}

for _, kind, payload in items:
    if kind == 'text':
        block = payload
        block = re.sub(r'\sstyle="[^"]*"', '', block)
        block = re.sub(r'\sclass="[^"]*"', '', block)
        block = re.sub(r'\sdata-rte-preserve-empty="[^"]*"', '', block)
        block = h1_re.sub('', block)

        years = year_re.findall(block)
        if years:
            current_year = years[0]
            if current_year not in sections:
                sections[current_year] = []
                order.append(current_year)
                seen_images_by_year[current_year] = set()
            block = year_re.sub('', block)

        if current_year is None:
            continue

        plain = re.sub(r'<[^>]+>', ' ', block).strip()
        if plain:
            sections[current_year].append(('html', block.strip()))

    else:
        if current_year is None:
            continue
        url = payload.replace('&amp;', '&').replace('\\u0026', '&').split('?format=')[0]
        if url not in ref_images:
            continue
        local = url_map.get(url)
        if not local:
            continue
        if local in seen_images_by_year[current_year]:
            continue
        seen_images_by_year[current_year].add(local)
        sections[current_year].append(('img', local))

parts = []
for year in order:
    content = sections[year]
    if not content:
        continue

    parts.append('  <section class="year-section">')
    parts.append(f'    <h2>{year}</h2>')

    img_index = 1
    for entry_type, value in content:
        if entry_type == 'html':
            parts.append(f'    {value}')
        else:
            parts.append('    <div class="gallery featured">')
            parts.append(f'      <img src="{value}" alt="{year} image {img_index}" loading="lazy">')
            parts.append('    </div>')
            img_index += 1

    parts.append('  </section>')

body = '\n'.join(parts)

out = f'''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>History | Friends of Bayside Trails</title>
  <meta name="description" content="Original, unabridged history timeline for the Bayside Trails.">
  <link rel="stylesheet" href="style.css">
</head>
<body>

{nav}

<main>
  <h1>History</h1>
{body}
</main>

{footer}

</body>
</html>
'''

out = re.sub(r'<p>\s*</p>', '', out)

history_path.write_text(out, encoding='utf-8')

img_count = sum(1 for y in order for t, _ in sections[y] if t == 'img')
print(f'Wrote history.html with {len(order)} year sections and {img_count} inline image placements')
