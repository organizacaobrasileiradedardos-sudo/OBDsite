#!/usr/bin/env python3
import re

file_path = 'obd/core/templates/index.html'

with open(file_path, 'r') as f:
    content = f.read()

# Regex to find the split tag: {{ followed by newline/whitespace, then doc.publish_date...
# We want to match: {{ \n\s+doc.publish_date|date:"d/m/Y" }}
# And replace with: {{ doc.publish_date|date:"d/m/Y" }}

pattern = r'{{\s*\n\s*doc\.publish_date\|date:"d/m/Y"\s*}}'
replacement = '{{ doc.publish_date|date:"d/m/Y" }}'

new_content = re.sub(pattern, replacement, content)

# Also try to catch if it's just a weird spacing issue on one line
pattern2 = r'{{\s+doc\.publish_date\|date:"d/m/Y"\s*}}'
new_content = re.sub(pattern2, replacement, new_content)

if content != new_content:
    print("Found and fixed the split tag!")
    with open(file_path, 'w') as f:
        f.write(new_content)
else:
    print("Pattern not found. Dumping context around 'doc.publish_date'...")
    match = re.search(r'.{20}doc\.publish_date.{20}', content, re.DOTALL)
    if match:
        print(f"Context: {match.group(0)!r}")
