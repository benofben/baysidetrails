import json
import pathlib

mapping = json.loads(pathlib.Path('assets/original-images-map.json').read_text(encoding='utf-8'))
urls = [
    u.strip()
    for u in pathlib.Path('tmp/history-image-urls.txt').read_text(encoding='utf-8').splitlines()
    if u.strip()
]

figures = []
for index, url in enumerate(urls, 1):
    local = mapping[url]
    figures.append(
        f'      <figure><img src="{local}" alt="History archive image {index}" loading="lazy"><figcaption>Image {index}</figcaption></figure>'
    )

body = "\n".join(figures)

content = f"""<!DOCTYPE html>
<html lang=\"en\">
<head>
  <meta charset=\"UTF-8\">
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">
  <title>History Image Archive | Friends of Bayside Trails</title>
  <meta name=\"description\" content=\"Complete archived image set from the original Bayside Trails history page.\">
  <link rel=\"stylesheet\" href=\"style.css\">
  <style>
    .archive-grid {{ display:grid; grid-template-columns: repeat(auto-fill, minmax(220px,1fr)); gap: 0.75rem; }}
    .archive-grid figure {{ margin:0; background:#f7f7f7; border:1px solid #ddd; border-radius:4px; overflow:hidden; }}
    .archive-grid img {{ width:100%; height:180px; object-fit:cover; display:block; }}
    .archive-grid figcaption {{ padding:0.45rem 0.55rem; font-size:0.75rem; color:#555; }}
  </style>
</head>
<body>
<nav>
  <div class=\"nav-inner\">
    <a class=\"site-title\" href=\"index.html\">Friends of Bayside Trails</a>
    <ul class=\"nav-links\">
      <li><a href=\"index.html\">Home</a></li>
      <li><a href=\"history.html\" class=\"active\">History</a></li>
      <li><a href=\"advocacy.html\">Advocacy</a></li>
      <li><a href=\"get-involved.html\">Get Involved</a></li>
    </ul>
  </div>
</nav>
<main>
  <h1>History Image Archive</h1>
  <p>This page contains every image URL extracted from the original <strong>History</strong> page and stored locally in this repository.</p>
  <p>Total archived images: {len(urls)}</p>
  <p><a href=\"history.html\">Back to History timeline</a></p>
  <section class=\"archive-grid\">
{body}
  </section>
</main>
<footer>
  <ul class=\"footer-links\">
    <li><a href=\"index.html\">Home</a></li>
    <li><a href=\"history.html\">History</a></li>
    <li><a href=\"advocacy.html\">Advocacy</a></li>
    <li><a href=\"get-involved.html\">Get Involved</a></li>
  </ul>
  <p>&copy; Friends of Bayside Trails &mdash; Tacoma, WA</p>
</footer>
</body>
</html>
"""

pathlib.Path('history-images.html').write_text(content, encoding='utf-8')
print(f'wrote history-images.html with {len(urls)} images')
