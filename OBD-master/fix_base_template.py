#!/usr/bin/env python3
import re

file_path = 'obd/core/templates/base.html'

with open(file_path, 'r') as f:
    content = f.read()

# Regex to find split tags: {% followed by newline/whitespace, then content, then %}
# We want to match: {% \n\s+ content \n\s* %} or similar variations

def fix_split_tags(match):
    full_tag = match.group(0)
    # Replace newlines and extra whitespace with a single space
    fixed_tag = re.sub(r'\s*\n\s*', ' ', full_tag)
    return fixed_tag

# Pattern for {% ... %} split across lines
pattern = r'{%[^%]*?\n[^%]*?%}'

new_content = re.sub(pattern, fix_split_tags, content)

if content != new_content:
    print(f"Fixed split tags in {file_path}")
    with open(file_path, 'w') as f:
        f.write(new_content)
else:
    print("No split tags found matching the pattern.")
