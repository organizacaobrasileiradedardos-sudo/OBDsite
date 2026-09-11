"""Procura nomes que uma função usa mas ninguém define — a família de erro do 'matches'.

Não substitui um pyflakes de verdade: ignora escopos aninhados e compreensões, e por
isso pode dar falso positivo. Serve para apontar onde olhar.
"""
import ast, builtins, sys, glob, os

EMBUTIDOS = set(dir(builtins)) | {'__name__', '__file__', '__doc__', 'self', 'cls'}


def definidos_no_modulo(arvore):
    nomes = set()
    for no in ast.walk(arvore):
        if isinstance(no, (ast.Import, ast.ImportFrom)):
            nomes |= {(a.asname or a.name).split('.')[0] for a in no.names}
        elif isinstance(no, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            nomes.add(no.name)
        elif isinstance(no, ast.Name) and isinstance(no.ctx, ast.Store):
            nomes.add(no.id)
        elif isinstance(no, ast.arg):
            nomes.add(no.arg)
        elif isinstance(no, ast.ExceptHandler) and no.name:
            nomes.add(no.name)
        elif isinstance(no, (ast.Global, ast.Nonlocal)):
            nomes |= set(no.names)
    return nomes


def verificar(caminho):
    origem = open(caminho, encoding='utf-8').read()
    try:
        arvore = ast.parse(origem)
    except SyntaxError as e:
        return [(e.lineno or 0, f'erro de sintaxe: {e.msg}')]

    conhecidos = definidos_no_modulo(arvore) | EMBUTIDOS
    achados = []
    for no in ast.walk(arvore):
        if isinstance(no, ast.Name) and isinstance(no.ctx, ast.Load) and no.id not in conhecidos:
            achados.append((no.lineno, no.id))
    return achados


alvos = sorted(f for f in glob.glob('obd/**/*.py', recursive=True) if '/migrations/' not in f)
total = 0
for f in alvos:
    for linha, nome in verificar(f):
        print(f'  {f}:{linha}  ->  {nome}')
        total += 1
print(f'\n{len(alvos)} arquivos analisados, {total} nome(s) possivelmente indefinido(s)')
