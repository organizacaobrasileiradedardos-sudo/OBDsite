#!/usr/bin/env python3
import re

# Read the file
with open('obd/core/templates/index.html', 'r') as f:
    content = f.read()

# Fix first multi-line if statement (lines 78-88)
pattern1 = r'{% if match\.result_set\.first\.player\.profile\.pin and\s+match\.result_set\.first\.player\.first_name and\s+match\.result_set\.first\.player\.last_name %}'
replacement1 = '{% if match.result_set.first.player.profile.pin and match.result_set.first.player.first_name and match.result_set.first.player.last_name %}'
content = re.sub(pattern1, replacement1, content)

# Fix second multi-line if statement (lines 93-103)
pattern2 = r'{% if match\.result_set\.last\.player\.profile\.pin and\s+match\.result_set\.last\.player\.first_name and\s+match\.result_set\.last\.player\.last_name %}'
replacement2 = '{% if match.result_set.last.player.profile.pin and match.result_set.last.player.first_name and match.result_set.last.player.last_name %}'
content = re.sub(pattern2, replacement2, content)

# Write back
with open('obd/core/templates/index.html', 'w') as f:
    f.write(content)

print("Template fixed successfully!")
