
import re
import os
import shutil
from datetime import datetime

# Configuration
FILES_TO_FIX = [
    'obd/core/templates/index.html',
    'obd/core/templates/profile_view.html'
]

def fix_file(file_path):
    if not os.path.exists(file_path):
        print(f"Skipping {file_path}: File not found.")
        return

    print(f"Processing {file_path}...")
    
    # Create a timestamped backup
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = f"{file_path}.{timestamp}.backup"
    shutil.copy2(file_path, backup_path)
    print(f"  - Backup created: {backup_path}")

    with open(file_path, 'r') as f:
        content = f.read()

    original_content = content

    # --- Fix Strategies ---

    # 1. Consolidate split {{ variable }} tags
    # Finds {{ followed by newlines/spaces, content, newlines/spaces, }}
    # and replaces with {{ content }}
    def consolidate_variable_tags(match):
        full_match = match.group(0)
        # Remove newlines and extra spaces
        cleaned = re.sub(r'\s+', ' ', full_match)
        cleaned = cleaned.replace('{{ ', '{{').replace(' }}', '}}')
        cleaned = cleaned.replace('{{', '{{ ').replace('}}', ' }}')
        return cleaned

    # Regex for split variables: {{ ... }} spanning multiple lines
    # We use a non-greedy match for content
    content = re.sub(r'{{\s+.*?\s+}}', consolidate_variable_tags, content, flags=re.DOTALL)


    # 2. Consolidate split {% if ... %} tags
    # Similar strategy for {% if ... %}
    def consolidate_block_tags(match):
        full_match = match.group(0)
        cleaned = re.sub(r'\s+', ' ', full_match)
        cleaned = cleaned.replace('{% ', '{%').replace(' %}', '%}')
        cleaned = cleaned.replace('{%', '{% ').replace('%}', ' %}')
        return cleaned

    content = re.sub(r'{%\s+if\s+.*?\s+%}', consolidate_block_tags, content, flags=re.DOTALL)
    content = re.sub(r'{%\s+endif\s+%}', '{% endif %}', content, flags=re.DOTALL)
    content = re.sub(r'{%\s+else\s+%}', '{% else %}', content, flags=re.DOTALL)
    content = re.sub(r'{%\s+for\s+.*?\s+%}', consolidate_block_tags, content, flags=re.DOTALL)
    content = re.sub(r'{%\s+endfor\s+%}', '{% endfor %}', content, flags=re.DOTALL)


    # 3. Specific Fixes for known problematic patterns in index.html
    
    # Fix Document Date quoting issue (double quotes to single quotes)
    content = re.sub(
        r"doc\.publish_date\|date:\"d/m/Y\"",
        "doc.publish_date|date:'d/m/Y'",
        content
    )

    # Fix Champion Name upper filter spacing
    content = re.sub(
        r"champion_name\|upper\s+}}",
        "champion_name|upper }}",
        content
    )

    # Fix the specific stats header block if it gets messed up again
    # This is a specific replacement for the known problematic block
    header_regex = r'<h3[^>]*>\s*<i[^>]*></i>\s*Estatísticas OBD\s*{%\s*if\s+tournament_stats\s*%}\s*<small[^>]*>\(\s*{{\s*tournament_stats\.name\s*}}\s*\)</small>\s*{%\s*endif\s*%}\s*</h3>'
    # It's hard to regex the whole block if it's very broken, but the general fixers above should handle the tags.
    # Let's just ensure no duplicate </h3> tags which was a symptom
    content = content.replace('{% endif %}</h3>\n                </h3>', '{% endif %}</h3>')


    # --- Write changes ---
    if content != original_content:
        with open(file_path, 'w') as f:
            f.write(content)
        print(f"  - FIXED: Issues resolved in {file_path}")
    else:
        print(f"  - No changes needed for {file_path}")

if __name__ == "__main__":
    print("Starting Template Fix Script...")
    print("This script will backup and fix known formatting issues in Django templates.")
    
    for file_path in FILES_TO_FIX:
        fix_file(file_path)
    
    print("\nDone! If issues persist, check the backups created.")
