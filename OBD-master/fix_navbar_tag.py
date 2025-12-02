#!/usr/bin/env python3
"""Fix split template tag in navbar greeting"""

file_path = 'obd/core/templates/base.html'

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# The problematic pattern that needs fixing
old_pattern = '''data-bs-toggle="dropdown" aria-expanded="false">Olá, {% if user.profile.nickname %}{{
                            user.profile.nickname }}{% else %}{{ user.first_name }} {{ user.last_name }}{% endif %}</a>'''

# The fixed version (all on one line)
new_pattern = '''data-bs-toggle="dropdown" aria-expanded="false">Olá, {% if user.profile.nickname %}{{ user.profile.nickname }}{% else %}{{ user.first_name }} {{ user.last_name }}{% endif %}</a>'''

if old_pattern in content:
    content = content.replace(old_pattern, new_pattern)
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"✓ Fixed navbar greeting tag in {file_path}")
else:
    print(f"✗ Pattern not found in {file_path}")
    print("Searching for variations...")
    # Try to find what's actually there
    if 'user.profile.nickname }}{% else %}' in content:
        print("Found the tag, but spacing might be different")
