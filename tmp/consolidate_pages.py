import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
URL_MAP = json.loads((ROOT / 'assets' / 'original-images-map.json').read_text(encoding='utf-8'))

PAGES = [
    ('index.html', 'home', 'Home', 'Friends of Bayside Trails'),
    ('advocacy.html', 'advocacy', 'Advocacy', 'Advocacy | Friends of Bayside Trails'),
    ('get-involved.html', 'get-involved', 'Get Involved', 'Get Involved | Friends of Bayside Trails'),
]


def extract_nav_footer(html: str) -> tuple[str, str]:
    nav_match = re.search(r'(<nav>[\s\S]*?</nav>)', html)
    footer_match = re.search(r'(<footer>[\s\S]*?</footer>)', html)
    if not nav_match or not footer_match:
        raise ValueError('Could not locate nav/footer')
    return nav_match.group(1), footer_match.group(1)


def clean_text_blocks(raw_source: str, output_name: str) -> list[str]:
    blocks = re.findall(r'<div class="sqs-html-content" data-sqsp-text-block-content>([\s\S]*?)</div>', raw_source)
    cleaned_blocks: list[str] = []

    for block in blocks:
        block = re.sub(r'\sstyle="[^"]*"', '', block)
        block = re.sub(r'\sclass="[^"]*"', '', block)
        block = re.sub(r'\sdata-rte-preserve-empty="[^"]*"', '', block)
        block = re.sub(r'<h1[^>]*>\s*[^<]*\s*</h1>', '', block, flags=re.IGNORECASE)
        block = re.sub(r'<p[^>]*>\s*</p>', '', block)

        if output_name == 'get-involved.html':
            if re.search(r'<h2[^>]*>\s*Vote\s*</h2>', block, flags=re.IGNORECASE):
                continue
            if re.search(r'Ben\s+Lackey\s+is\s+running\s+for\s+Tacoma\s+City\s+Council', block, flags=re.IGNORECASE):
                continue
            if 'https://benlackey.com/platform' in block:
                continue

        plain_text = re.sub(r'<[^>]+>', ' ', block).strip()
        if plain_text:
            cleaned_blocks.append(block.strip())

    return cleaned_blocks


def collect_local_images(raw_source: str) -> list[str]:
    image_urls = re.findall(r'https://images\.squarespace-cdn\.com[^"\s)<>]+', raw_source)
    local_images: list[str] = []
    seen: set[str] = set()

    for image_url in image_urls:
        normalized = image_url.replace('&amp;', '&').replace('\\u0026', '&')
        base_url = normalized.split('?format=')[0]
        if base_url in seen:
            continue
        seen.add(base_url)
        local_path = URL_MAP.get(base_url)
        if local_path:
            local_images.append(local_path)

    return local_images


def build_page_html(nav_html: str, footer_html: str, page_h1: str, page_title: str, body_blocks: list[str], local_images: list[str]) -> str:
    text_html = '\n'.join(body_blocks)

    images_section = ''
    if local_images:
        figures = '\n'.join(
            f'      <figure><img src="{image}" alt="{page_h1} original image {index}" loading="lazy"></figure>'
            for index, image in enumerate(local_images, 1)
        )
        images_section = f'''

  <section class="year-section">
    <h2>Original Images</h2>
    <section class="archive-grid">
{figures}
    </section>
  </section>'''

    return f'''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{page_title}</title>
  <meta name="description" content="Original, unabridged content for the {page_h1.lower()} page.">
  <link rel="stylesheet" href="style.css">
  <style>
    .page-original p, .page-original li {{ line-height: 1.5; }}
    .page-original h2 {{ margin-top: 1.75rem; }}
    .archive-grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(220px, 1fr)); gap: 0.75rem; }}
    .archive-grid figure {{ margin: 0; background: #f7f7f7; border: 1px solid #ddd; border-radius: 4px; overflow: hidden; }}
    .archive-grid img {{ width: 100%; height: 180px; object-fit: cover; display: block; }}
  </style>
</head>
<body>

{nav_html}

<main>
  <h1>{page_h1}</h1>

  <section class="year-section">
    <h2>Original Content (Unabridged)</h2>
    <div class="page-original">
{text_html}
    </div>
  </section>{images_section}
</main>

{footer_html}

</body>
</html>
'''


def main() -> None:
    for output_name, source_slug, page_h1, page_title in PAGES:
        output_path = ROOT / output_name
        source_path = ROOT / 'tmp' / f'page-{source_slug}.html'

        current_html = output_path.read_text(encoding='utf-8')
        source_html = source_path.read_text(encoding='utf-8', errors='ignore')

        nav_html, footer_html = extract_nav_footer(current_html)
        body_blocks = clean_text_blocks(source_html, output_name)
        local_images = collect_local_images(source_html)

        updated_html = build_page_html(nav_html, footer_html, page_h1, page_title, body_blocks, local_images)
        output_path.write_text(updated_html, encoding='utf-8')
        print(f'Updated {output_name}: blocks={len(body_blocks)} images={len(local_images)}')


if __name__ == '__main__':
    main()
