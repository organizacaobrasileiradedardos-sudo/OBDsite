#!/usr/bin/env python3
"""Correção com os padrões EXATOS das linhas 251-254"""

filepath = '/Users/mac2/Documents/Backup Pen Drive - Janeiro 2025/Coisa Minha/DARDO/OBD/Projeto Site OBD/OBD-master/obd/core/templates/index.html'

with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# Padrão EXATO da linha 251-254 (Média Geral)
old1 = '''                                <li class="list-group-item d-flex justify-content-between align-items-center">Média
                                    Geral <span class="badge bg-primary rounded-pill">{% if tournament_stats %}{{
                                        tournament_stats.average|floatformat:"2" }}{% else %}{% if boa.average %}{{
                                        boa.average|floatformat:"2" }}{% else %}0{% endif %}{% endif %}</span></li>'''
new1 = '''                                <li class="list-group-item d-flex justify-content-between align-items-center">Média Geral <span class="badge bg-primary rounded-pill">{% if tournament_stats %}{{ tournament_stats.average|floatformat:"2" }}{% else %}{% if boa.average %}{{ boa.average|floatformat:"2" }}{% else %}0{% endif %}{% endif %}</span></li>'''

# Padrão EXATO da linha 255-257 (Partidas)
old2 = '''                                <li class="list-group-item d-flex justify-content-between align-items-center">Partidas
                                    <span class="badge bg-primary rounded-pill">{% if tournament_stats %}{{
                                        tournament_stats.matches }}{% else %}{{ games|default:"0" }}{% endif %}</span>'''
new2 = '''                                <li class="list-group-item d-flex justify-content-between align-items-center">Partidas <span class="badge bg-primary rounded-pill">{% if tournament_stats %}{{ tournament_stats.matches }}{% else %}{{ games|default:"0" }}{% endif %}</span>'''

# Padrão EXATO da linha 259-261 (Legs)
old3 = '''                                <li class="list-group-item d-flex justify-content-between align-items-center">Legs <span
                                        class="badge bg-primary rounded-pill">{% if tournament_stats %}{{
                                        tournament_stats.legs }}{% else %}{{ boa.legs|default:"0" }}{% endif %}</span>'''
new3 = '''                                <li class="list-group-item d-flex justify-content-between align-items-center">Legs <span class="badge bg-primary rounded-pill">{% if tournament_stats %}{{ tournament_stats.legs }}{% else %}{{ boa.legs|default:"0" }}{% endif %}</span>'''

# Padrão EXATO da linha 263-265 (Jogadores)
old4 = '''                                <li class="list-group-item d-flex justify-content-between align-items-center">Jogadores
                                    <span class="badge bg-primary rounded-pill">{% if tournament_stats %}{{
                                        tournament_stats.players }}{% else %}{{ members|default:"0" }}{% endif %}</span>'''
new4 = '''                                <li class="list-group-item d-flex justify-content-between align-items-center">Jogadores <span class="badge bg-primary rounded-pill">{% if tournament_stats %}{{ tournament_stats.players }}{% else %}{{ members|default:"0" }}{% endif %}</span>'''

# Aplicar todas as correções
fixes_applied = 0
if old1 in content:
    content = content.replace(old1, new1)
    fixes_applied += 1
    print("✓ Média Geral corrigida")

if old2 in content:
    content = content.replace(old2, new2)
    fixes_applied += 1
    print("✓ Partidas corrigida")

if old3 in content:
    content = content.replace(old3, new3)
    fixes_applied += 1
    print("✓ Legs corrigida")

if old4 in content:
    content = content.replace(old4, new4)
    fixes_applied += 1
    print("✓ Jogadores corrigida")

# Salvar
with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)

print(f"\n✅ {fixes_applied} correções aplicadas!")
