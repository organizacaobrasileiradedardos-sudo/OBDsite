#!/usr/bin/env python3
"""Fix all split template tags in index.html"""

# Read the file
with open('/Users/mac2/Documents/Backup Pen Drive - Janeiro 2025/Coisa Minha/DARDO/OBD/Projeto Site OBD/OBD-master/obd/core/templates/index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Fix split `{% if tournament_stats %}` tag on lines 244-245
content = content.replace(
    '<h3 class="text-center mb-4 fw-bold"><i class="bi bi-graph-up text-accent"></i> Estatísticas OBD {% if\n                    tournament_stats %}<small class="text-muted fs-6">({{ tournament_stats.name }})</small>{% endif %}',
    '<h3 class="text-center mb-4 fw-bold"><i class="bi bi-graph-up text-accent"></i> Estatísticas OBD {% if tournament_stats %}<small class="text-muted fs-6">({{ tournament_stats.name }})</small>{% endif %}'
)

# Write back
with open('/Users/mac2/Documents/Backup Pen Drive - Janeiro 2025/Coisa Minha/DARDO/OBD/Projeto Site OBD/OBD-master/obd/core/templates/index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("Fixed index.html template tags")
