#!/usr/bin/env python3
"""Comprehensive fix for all template tags in profile_view.html"""
import re

# Read the file
with open('/Users/mac2/Documents/Backup Pen Drive - Janeiro 2025/Coisa Minha/DARDO/OBD/Projeto Site OBD/OBD-master/obd/core/templates/profile_view.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Find and fix all split template tags
# Fix pattern 1: {% if ... %} ... {% else ... %} ... {% endif %}
content = re.sub(
    r'{%\s*if\s+([^%]+)%}\s*value="([^"]+)"\s*{%\s*else\s*%}\s*value="([^"]+)"\s*{%\s*endif\s*%}',
    r'{% if \1%} value="\2" {% else %} value="\3" {% endif %}',
    content
)

# Fix pattern 2: Split endif tags
content = re.sub(
    r'{%\s*endif\s+%}',
    r'{% endif %}',
    content
)

# Fix pattern 3: Tags split across lines with extra whitespace
lines = content.split('\n')
fixed_lines = []
i = 0

while i < len(lines):
    line = lines[i]
    
    # Check if this line has an unclosed {% if
    if '{% if' in line and '%}' not in line.split('{% if')[1].split('{%')[0]:
        # This if tag is split, merge with next lines until we find the closing %}
        merged = line
        i += 1
        while i < len(lines) and '%}' not in merged.split('{% if')[-1]:
            merged += ' ' + lines[i].strip()
            i += 1
        fixed_lines.append(merged)
    # Check if endif is split
    elif '{% endif' in line and not line.strip().endswith('%}'):
        # endif is split
        merged = line
        i += 1
        while i < len(lines) and not merged.strip().endswith('%}'):
            merged = merged.rstrip() + lines[i].strip()
            i += 1
        # Make sure it's properly formatted
        merged = re.sub(r'{%\s*endif\s*%}', '{% endif %}', merged)
        fixed_lines.append(merged)
    else:
        fixed_lines.append(line)
        i += 1

content = '\n'.join(fixed_lines)

# Additional cleanup: ensure all {% endif %} are properly closed
content = re.sub(r'{%\s*endif\s*$', '{% endif %}', content, flags=re.MULTILINE)

# Write back
with open('/Users/mac2/Documents/Backup Pen Drive - Janeiro 2025/Coisa Minha/DARDO/OBD/Projeto Site OBD/OBD-master/obd/core/templates/profile_view.html', 'w', encoding='utf-8') as f:
    f.write(content)

# Count if/endif to verify
if_count = len(re.findall(r'{%\s*if\s+', content))
endif_count = len(re.findall(r'{%\s*endif\s*%}', content))

print(f"Fixed profile_view.html")
print(f"{{% if count: {if_count}")
print(f"{{% endif count: {endif_count}")
if if_count == endif_count:
    print("✓ Tags are balanced!")
else:
    print(f"✗ WARNING: Tags are NOT balanced! Difference: {if_count - endif_count}")
