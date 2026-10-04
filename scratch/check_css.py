import re

with open('app.py', encoding='utf-8') as f:
    app_text = f.read()

classes_in_app = set(re.findall(r'class=[\'"]([^\'"]+)[\'"]', app_text))
all_classes_split = set()
for c in classes_in_app:
    for sub in c.split():
        all_classes_split.add(sub)

print('Classes used in app.py:')
with open('assets/style.css', encoding='utf-8') as f:
    css_text = f.read()

missing = []
for c in sorted(all_classes_split):
    if f'.{c}' not in css_text:
        missing.append(c)
        print(' [MISSING]', c)
    else:
        print(' [FOUND]', c)

print('\nTotal missing classes:', len(missing))
