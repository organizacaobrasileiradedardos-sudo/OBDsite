#!/usr/bin/env python3
"""
███████╗ ██████╗ ██╗     ██╗   ██╗ ██████╗  █████╗  ██████╗     ██████╗ ███████╗███████╗██╗███╗   ██╗██╗████████╗██╗██╗   ██╗ █████╗ 
██╔════╝██╔═══██╗██║     ██║   ██║██╔════╝ ██╔══██╗██╔═══██╗    ██╔══██╗██╔════╝██╔════╝██║████╗  ██║██║╚══██╔══╝██║██║   ██║██╔══██╗
███████╗██║   ██║██║     ██║   ██║██║  ███╗███████║██║   ██║    ██║  ██║█████╗  █████╗  ██║██╔██╗ ██║██║   ██║   ██║██║   ██║███████║
╚════██║██║   ██║██║     ██║   ██║██║   ██║██╔══██║██║   ██║    ██║  ██║██╔══╝  ██╔══╝  ██║██║╚██╗██║██║   ██║   ██║╚██╗ ██╔╝██╔══██║
███████║╚██████╔╝███████╗╚██████╔╝╚██████╔╝██║  ██║╚██████╔╝    ██████╔╝███████╗██║     ██║██║ ╚████║██║   ██║   ██║ ╚████╔╝ ██║  ██║
╚══════╝ ╚═════╝ ╚══════╝ ╚═════╝  ╚═════╝ ╚═╝  ╚═╝ ╚═════╝     ╚═════╝ ╚══════╝╚═╝     ╚═╝╚═╝  ╚═══╝╚═╝   ╚═╝   ╚═╝  ╚═══╝  ╚═╝  ╚═╝

Este script corrige DEFINITIVAMENTE TODOS os problemas de tags Django divididas em index.html.
Execute este arquivo sempre que as estatísticas desaparecerem.

Autor: Antigravity AI
Data: 2025-11-23
"""

import re

print("🔧 Iniciando correção definitiva do index.html...")
print("=" * 80)

# Ler o arquivo
filepath = '/Users/mac2/Documents/Backup Pen Drive - Janeiro 2025/Coisa Minha/DARDO/OBD/Projeto Site OBD/OBD-master/obd/core/templates/index.html'
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# Contador de correções
fixes = 0

# 1. Corrigir título do campeão (se dividido)
old = 'Campeão do Campeonato Brasileiro\n                            de Dardos OBD 2025'
new = 'Campeão do Campeonato Brasileiro de Dardos OBD 2025'
if old in content:
    content = content.replace(old, new)
    fixes += 1
    print("✅ Título do campeão consolidado")

# 2. Corrigir nome do campeão (se dividido)
old = '{{ tournament_stats.champion_name|upper\n                            }}'
new = '{{ tournament_stats.champion_name|upper }}'
if old in content:
    content = content.replace(old, new)
    fixes += 1
    print("✅ Nome do campeão consolidado")

# 3. Consolidar TODAS as tags de estatísticas usando regex
# Padrão: encontra tags {{ ... }} divididas em múltiplas linhas
pattern = r'\{\{([^}]+)\n\s+([^}]+)\}\}'
def consolidate_tag(match):
    return '{{ ' + match.group(1).strip() + ' ' + match.group(2).strip() + ' }}'

before_count = len(re.findall(pattern, content))
if before_count > 0:
    content = re.sub(pattern, consolidate_tag, content)
    fixes += before_count
    print(f"✅ {before_count} tags de variáveis consolidadas")

# 4. Consolidar tags {% if %} divididas
pattern = r'\{%\s*if([^%]+)\n\s+([^%]+)%\}'
def consolidate_if(match):
    return '{% if' + match.group(1).strip() + ' ' + match.group(2).strip() + ' %}'

before_count = len(re.findall(pattern, content))
if before_count > 0:
    content = re.sub(pattern, consolidate_if, content)
    fixes += before_count
    print(f"✅ {before_count} tags {{% if %}} consolidadas")

# 5. Consolidar tags {% else %} e {% endif %} divididas
for tag in ['else', 'endif']:
    pattern = fr'\{%\s*{tag}([^%]*)\n\s+([^%]*)%\}'
    before_count = len(re.findall(pattern, content))
    if before_count > 0:
        content = re.sub(pattern, f'{{% {tag} %}}', content)
        fixes += before_count
        print(f"✅ {before_count} tags {{% {tag} %}} consolidadas")

# 6. Remover espaços extras dentro das tags
content = re.sub(r'\{\{\s+', '{{ ', content)
content = re.sub(r'\s+\}\}', ' }}', content)
content = re.sub(r'\{%\s+', '{% ', content)
content = re.sub(r'\s+%\}', ' %}', content)

# Escrever de volta
with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)

print("=" * 80)
print(f"✅ CONCLUÍDO! Total de {fixes} correções aplicadas.")
print()
print("📋 O QUE FOI CORRIGIDO:")
print("   • Título do campeão")
print("   • Nome do campeão")
print("   • Tags de estatísticas (Média Geral, Partidas, Legs, Jogadores)")
print("   • Tags de scores (100+, 140+, 170+, 180)")
print("   • Tags de recordes (Maior Fechamento, Melhor Leg, Melhor Média)")
print()
print("💡 COMO USAR NO FUTURO:")
print("   Se as estatísticas desaparecerem novamente, execute:")
print("   python3 fix_index_definitivo.py")
print()
print("🎯 DICA: Para evitar esse problema, sempre mantenha as tags Django")
print("   em uma única linha quando editar o arquivo manualmente.")
