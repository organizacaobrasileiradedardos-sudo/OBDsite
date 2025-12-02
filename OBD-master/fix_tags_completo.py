#!/usr/bin/env python3
"""Correção COMPLETA: Dados Gerais, Scores, Recordes e Campeão"""

filepath = '/Users/mac2/Documents/Backup Pen Drive - Janeiro 2025/Coisa Minha/DARDO/OBD/Projeto Site OBD/OBD-master/obd/core/templates/index.html'

with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

fixes_applied = 0

# ============= SCORES =============
# 140+ (linhas 270-271)
old = '''140+ <span
                                        class="badge bg-primary rounded-pill">{% if tournament_stats %}{{
                                        tournament_stats.ton40 }}{% else %}{{ boa.ton40|default:"0" }}{% endif %}</span>'''
new = '''140+ <span class="badge bg-primary rounded-pill">{% if tournament_stats %}{{ tournament_stats.ton40 }}{% else %}{{ boa.ton40|default:"0" }}{% endif %}</span>'''
if old in content:
    content = content.replace(old, new)
    fixes_applied += 1
    print("✓ 140+ corrigido")

# 170+ (linhas 274-275)
old = '''170+ <span
                                        class="badge bg-primary rounded-pill">{% if tournament_stats %}{{
                                        tournament_stats.ton70 }}{% else %}{{ boa.ton70|default:"0" }}{% endif %}</span>'''
new = '''170+ <span class="badge bg-primary rounded-pill">{% if tournament_stats %}{{ tournament_stats.ton70 }}{% else %}{{ boa.ton70|default:"0" }}{% endif %}</span>'''
if old in content:
    content = content.replace(old, new)
    fixes_applied += 1
    print("✓ 170+ corrigido")

# 180s (linhas 278-279)
old = '''180s <span
                                        class="badge bg-danger rounded-pill">{% if tournament_stats %}{{
                                        tournament_stats.ton80 }}{% else %}{{ boa.ton80|default:"0" }}{% endif %}</span>'''
new = '''180s <span class="badge bg-danger rounded-pill">{% if tournament_stats %}{{ tournament_stats.ton80 }}{% else %}{{ boa.ton80|default:"0" }}{% endif %}</span>'''
if old in content:
    content = content.replace(old, new)
    fixes_applied += 1
    print("✓ 180s corrigido")

# ============= RECORDES =============
# Maior Fechamento (linhas 288-290)
old = '''Maior
                                    Fechamento <span class="badge bg-primary rounded-pill">{{
                                        tournament_stats.highest_out }}</span>'''
new = '''Maior Fechamento <span class="badge bg-primary rounded-pill">{{ tournament_stats.highest_out }}</span>'''
if old in content:
    content = content.replace(old, new)
    fixes_applied += 1
    print("✓ Maior Fechamento corrigido")

# Melhor Média (linhas 295-297)
old = '''Melhor
                                    Média <span class="badge bg-primary rounded-pill">{{
                                        tournament_stats.best_avg|floatformat:"2" }}</span>'''
new = '''Melhor Média <span class="badge bg-primary rounded-pill">{{ tournament_stats.best_avg|floatformat:"2" }}</span>'''
if old in content:
    content = content.replace(old, new)
    fixes_applied += 1
    print("✓ Melhor Média corrigido")

# ============= CAMPEÃO =============
# Nome do campeão (linhas 324-325)
old = '''{{ tournament_stats.champion_name|upper
                            }}'''
new = '''{{ tournament_stats.champion_name|upper }}'''
if old in content:
    content = content.replace(old, new)
    fixes_applied += 1
    print("✓ Nome do campeão corrigido")

# Salvar
with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)

print(f"\n✅ {fixes_applied} correções aplicadas com sucesso!")
print("\n📊 Seções corrigidas:")
print("   • Scores (140+, 170+, 180s)")
print("   • Recordes (Maior Fechamento, Melhor Média)")
print("   • Nome do Campeão")
