#!/usr/bin/env python3
"""Fix all malformed template tags in profile_view.html"""

# Read the file
with open('/Users/mac2/Documents/Backup Pen Drive - Janeiro 2025/Coisa Minha/DARDO/OBD/Projeto Site OBD/OBD-master/obd/core/templates/profile_view.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Fix line 60-62: birthdate field
i = 59  # 0-indexed for line 60
if i < len(lines):
    # Combine lines 60-62 into a proper single-line expression
    combined = lines[i].rstrip() + ' ' + lines[i+1].strip() + ' ' + lines[i+2].strip()
    combined = combined.replace('{% endif\n                %}', '{% endif %}')
    combined = combined.replace('{% endif %}>', '{% endif %}')
    lines[i] = '                name="{{ form.birthdate.html_name}}" {% if form.birthdate.value is not None %} value="{{ form.birthdate.value}}" {% else %} value="{{ profile.birth_date | date:\'Y-m-d\' }}" {% endif %}>\n'
    del lines[i+1:i+3]  # Remove the broken continuation lines

# Fix around line 139 (now shifted): site field
for i in range(len(lines)):
    if 'form.site.html_name' in lines[i] and '{% if' in lines[i]:
        if i+1 < len(lines) and 'endif' in lines[i+1]:
            # Merge the lines
            lines[i] = lines[i].rstrip() + ' ' + lines[i+1].strip() + '\n'
            lines[i] = lines[i].replace('{% endif %}>', '{% endif %}')
            lines[i] = lines[i].replace('{% endif            %>', '{% endif %}')
            del lines[i+1]
            break

# Fix around line 197 (now shifted): nationalfederation field  
for i in range(len(lines)):
    if 'form.nationalfederation.html_name' in lines[i] and '{% if' in lines[i]:
        if i+1 < len(lines) and i+2 < len(lines) and 'endif' in lines[i+2]:
            # Merge three lines
            lines[i] = lines[i].rstrip() + ' ' + lines[i+1].strip() + ' ' + lines[i+2].strip() + '\n'
            lines[i] = lines[i].replace('{% endif\n                %}', '{% endif %}')
            lines[i] = lines[i].replace('{% endif %}>', '{% endif %}')
            del lines[i+1:i+3]
            break

# Write back
with open('/Users/mac2/Documents/Backup Pen Drive - Janeiro 2025/Coisa Minha/DARDO/OBD/Projeto Site OBD/OBD-master/obd/core/templates/profile_view.html', 'w', encoding='utf-8') as f:
    f.writelines(lines)

print("Fixed profile_view.html template tags")
