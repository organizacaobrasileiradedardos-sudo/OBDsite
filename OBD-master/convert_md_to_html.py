#!/usr/bin/env python3
import re

# Lê o arquivo markdown
md_path = '/Users/mac2/.gemini/antigravity/brain/636ef1ec-7471-45b5-bd09-455df61de0a6/implementation_plan.md'
with open(md_path, 'r', encoding='utf-8') as f:
    md_content = f.read()

# Conversão de Markdown para HTML
html_content = md_content

# Títulos
html_content = re.sub(r'^# (.*?)$', r'<h1>\1</h1>', html_content, flags=re.MULTILINE)
html_content = re.sub(r'^## (.*?)$', r'<h2>\1</h2>', html_content, flags=re.MULTILINE)
html_content = re.sub(r'^### (.*?)$', r'<h3>\1</h3>', html_content, flags=re.MULTILINE)
html_content = re.sub(r'^#### (.*?)$', r'<h4>\1</h4>', html_content, flags=re.MULTILINE)

# Blocos de código
html_content = re.sub(r'```python\n(.*?)```', r'<pre><code class="language-python">\1</code></pre>', html_content, flags=re.DOTALL)
html_content = re.sub(r'```bash\n(.*?)```', r'<pre><code class="language-bash">\1</code></pre>', html_content, flags=re.DOTALL)
html_content = re.sub(r'```(.*?)```', r'<pre><code>\1</code></pre>', html_content, flags=re.DOTALL)

# Negrito e itálico
html_content = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', html_content)
html_content = re.sub(r'\*(.*?)\*', r'<em>\1</em>', html_content)

# Código inline
html_content = re.sub(r'`(.*?)`', r'<code>\1</code>', html_content)

# Links
html_content = re.sub(r'\[([^\]]+)\]\(([^\)]+)\)', r'<a href="\2">\1</a>', html_content)

# Linhas horizontais
html_content = re.sub(r'^---$', r'<hr>', html_content, flags=re.MULTILINE)

# Emojis especiais
html_content = html_content.replace('✅', '<span style="color: green;">✅</span>')
html_content = html_content.replace('⚠️', '<span style="color: orange;">⚠️</span>')
html_content = html_content.replace('🔴', '<span style="color: red;">🔴</span>')
html_content = html_content.replace('⚡', '<span style="color: gold;">⚡</span>')

# Processar listas e parágrafos
lines = html_content.split('\n')
new_lines = []
in_list = False
in_code = False
in_table = False

for line in lines:
    if '<pre>' in line:
        in_code = True
    if '</pre>' in line:
        in_code = False
        
    if in_code:
        new_lines.append(line)
        continue
    
    # Tabelas
    if '|' in line and not line.startswith('<'):
        if not in_table:
            new_lines.append('<table>')
            in_table = True
            # Header row
            cells = [c.strip() for c in line.split('|')[1:-1]]
            new_lines.append('<thead><tr>')
            for cell in cells:
                new_lines.append(f'<th>{cell}</th>')
            new_lines.append('</tr></thead>')
            continue
        elif '---' in line:
            new_lines.append('<tbody>')
            continue
        else:
            cells = [c.strip() for c in line.split('|')[1:-1]]
            new_lines.append('<tr>')
            for cell in cells:
                new_lines.append(f'<td>{cell}</td>')
            new_lines.append('</tr>')
            continue
    elif in_table and '|' not in line:
        new_lines.append('</tbody></table>')
        in_table = False
    
    # Listas
    if line.startswith('- '):
        if not in_list:
            new_lines.append('<ul>')
            in_list = True
        new_lines.append(f'<li>{line[2:]}</li>')
    else:
        if in_list:
            new_lines.append('</ul>')
            in_list = False
        
        if line.strip() and not line.startswith('<'):
            # Blockquotes especiais
            if line.startswith('> [!WARNING]'):
                new_lines.append('<div class="warning"><strong>⚠️ WARNING</strong>')
            elif line.startswith('> [!IMPORTANT]'):
                new_lines.append('<div class="important"><strong>ℹ️ IMPORTANT</strong>')
            elif line.startswith('> '):
                if not new_lines[-1].startswith('<div class='):
                    new_lines.append('<blockquote>')
                new_lines.append(f'<p>{line[2:]}</p>')
            elif new_lines and (new_lines[-1].startswith('<div class="warning') or new_lines[-1].startswith('<div class="important')):
                if line.strip():
                    new_lines.append(f'<p>{line}</p>')
                else:
                    new_lines.append('</div>')
            else:
                new_lines.append(f'<p>{line}</p>')
        else:
            new_lines.append(line)

if in_list:
    new_lines.append('</ul>')
if in_table:
    new_lines.append('</tbody></table>')

html_body = '\n'.join(new_lines)

# Template HTML completo
html_template = f'''<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Plano de Implementação - Remoção de Plataformas Externas</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            line-height: 1.6;
            max-width: 1000px;
            margin: 0 auto;
            padding: 40px 20px;
            color: #333;
            background-color: #f8f9fa;
        }}
        
        h1 {{
            color: #1a1a1a;
            border-bottom: 4px solid #007bff;
            padding-bottom: 15px;
            margin: 30px 0 20px 0;
            font-size: 2.5em;
        }}
        
        h2 {{
            color: #2c3e50;
            border-bottom: 2px solid #6c757d;
            padding-bottom: 10px;
            margin-top: 40px;
            margin-bottom: 20px;
            font-size: 2em;
        }}
        
        h3 {{
            color: #495057;
            margin-top: 30px;
            margin-bottom: 15px;
            font-size: 1.5em;
        }}
        
        h4 {{
            color: #6c757d;
            margin-top: 20px;
            margin-bottom: 10px;
            font-size: 1.2em;
        }}
        
        p {{
            margin: 10px 0;
            text-align: justify;
        }}
        
        code {{
            background-color: #f4f4f4;
            padding: 2px 8px;
            border-radius: 4px;
            font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
            font-size: 0.9em;
            color: #d63384;
        }}
        
        pre {{
            background-color: #f8f9fa;
            border: 1px solid #dee2e6;
            border-left: 4px solid #007bff;
            padding: 20px;
            border-radius: 6px;
            overflow-x: auto;
            margin: 20px 0;
        }}
        
        pre code {{
            background: none;
            padding: 0;
            color: #212529;
            font-size: 0.875em;
            line-height: 1.5;
        }}
        
        table {{
            border-collapse: collapse;
            width: 100%;
            margin: 25px 0;
            background-color: white;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        
        th, td {{
            border: 1px solid #dee2e6;
            padding: 12px 15px;
            text-align: left;
        }}
        
        th {{
            background-color: #007bff;
            color: white;
            font-weight: 600;
        }}
        
        tr:nth-child(even) {{
            background-color: #f8f9fa;
        }}
        
        tr:hover {{
            background-color: #e9ecef;
        }}
        
        ul {{
            margin: 15px 0;
            padding-left: 30px;
        }}
        
        li {{
            margin: 8px 0;
        }}
        
        hr {{
            border: none;
            border-top: 2px solid #dee2e6;
            margin: 40px 0;
        }}
        
        .warning {{
            background-color: #fff3cd;
            border-left: 5px solid #ffc107;
            padding: 20px;
            margin: 25px 0;
            border-radius: 4px;
        }}
        
        .important {{
            background-color: #d1ecf1;
            border-left: 5px solid #0dcaf0;
            padding: 20px;
            margin: 25px 0;
            border-radius: 4px;
        }}
        
        blockquote {{
            border-left: 4px solid #6c757d;
            padding-left: 20px;
            margin: 20px 0;
            color: #495057;
            font-style: italic;
        }}
        
        a {{
            color: #007bff;
            text-decoration: none;
        }}
        
        a:hover {{
            text-decoration: underline;
        }}
        
        footer {{
            margin-top: 60px;
            padding-top: 30px;
            border-top: 2px solid #dee2e6;
            text-align: center;
            color: #6c757d;
            font-size: 0.9em;
        }}
        
        @media print {{
            body {{
                background-color: white;
                margin: 0;
                padding: 20px;
            }}
            
            .warning, .important {{
                page-break-inside: avoid;
            }}
        }}
    </style>
</head>
<body>
{html_body}

<footer>
    <p><strong>OBD - Organização Brasileira de Dardos</strong></p>
    <p>Documento gerado em: 24 de Novembro de 2025</p>
</footer>
</body>
</html>'''

# Salva o HTML
output_path = '/Users/mac2/Documents/Backup Pen Drive - Janeiro 2025/Coisa Minha/DARDO/OBD/Projeto Site OBD/Planos de Implementação/Plano_Remocao_Plataformas_Externas.html'
with open(output_path, 'w', encoding='utf-8') as f:
    f.write(html_template)

print(f"✅ Arquivo HTML criado com sucesso!")
print(f"📄 Local: {output_path}")
print(f"📊 Tamanho: {len(html_template):,} bytes")
