import json
import pathlib

history_path = pathlib.Path('history.html')
mapping = json.loads(pathlib.Path('assets/original-images-map.json').read_text(encoding='utf-8'))
text = history_path.read_text(encoding='utf-8')

replacements = 0
for remote, local in mapping.items():
    if remote in text:
        text = text.replace(remote, local)
        replacements += 1

history_path.write_text(text, encoding='utf-8')
print(f'replacements {replacements}')
